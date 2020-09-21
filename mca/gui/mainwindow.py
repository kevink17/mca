from PySide2 import QtWidgets, QtCore, QtGui
import os
import ntpath

import mca.blocks
from mca.framework import block_registry
from mca.gui import block_list, block_display, block_item
from mca import config
from mca.language import _


class MainWindow(QtWidgets.QMainWindow):
    """Main window of the mca. Holds the main widgets of the application.

    Attributes:
        menu: Menu bar of the application.
        file_menu: File menu.
        language_menu: Language menu.
        main_widget: Splitter widget to split the :class:`.BlockList` and the
                     :class:`.BlockScene`.
        scene: :class:`.BlockScene` to manage and hold blocks.
        view: :class:`.BlockView` to visualize the items of the
              :class:`.BlockScene`.
    """

    def __init__(self):
        """Initialize MainWindow."""
        QtWidgets.QMainWindow.__init__(self)
        self.resize(1000, 800)

        self.conf = config.Config()

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu(_("File"))
        self.language_menu = self.menu.addMenu(_("Language"))
        languages = [("Deutsch", "de"), ("English", "en")]

        self.setWindowIcon(QtGui.QIcon(
            os.path.dirname(mca.blocks.__file__) + "/icons/emt_logo.png"))
        for i in languages:
            action = QtWidgets.QAction(i[0], self)
            action.triggered.connect(change_language(i[1]))
            self.language_menu.addAction(action)

        clear_action = QtWidgets.QAction(_("Clear"), self)
        clear_action.triggered.connect(self.clear)
        self.file_menu.addAction(clear_action)

        open_action = QtWidgets.QAction(_("Open"), self)
        open_action.triggered.connect(self.open_file_dialog)
        self.file_menu.addAction(open_action)

        self.open_recent_menu = QtWidgets.QMenu(_("Open Recent"), self)
        self.update_recent_menu()

        self.file_menu.addMenu(self.open_recent_menu)

        save_action = QtWidgets.QAction(_("Save"), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        self.save_file_path = None
        self.file_menu.addAction(save_action)

        save_as_action = QtWidgets.QAction(_("Save as"), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(save_as_action)

        exit_action = QtWidgets.QAction(_("Exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip(_("Close Application"))
        exit_action.triggered.connect(self.exit_app)
        self.file_menu.addAction(exit_action)

        self.modified = False

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.block_classes = mca.blocks.block_classes
        self.scene = block_display.BlockScene(self.main_widget)
        self.block_list = block_list.BlockList(self, self.block_classes,
                                               self.scene)
        self.main_layout.addWidget(self.block_list)
        self.view = block_display.BlockView(scene=self.scene, parent=self)
        self.view.show()
        self.main_layout.addWidget(self.view)
        self.setCentralWidget(self.main_widget)

    @QtCore.Slot()
    def exit_app(self):
        """Quit the application."""
        QtWidgets.QApplication.quit()

    def closeEvent(self, event):
        """Called when the application gets closed. Ask the user to save
        unsaved changes.
        """
        if self.save_maybe():
            event.accept()
        else:
            event.ignore()

    def open_file_dialog(self):
        """Opens file dialog to let the user select a file to open."""
        if self.save_maybe():
            file_name = QtWidgets.QFileDialog.getOpenFileName(
                self, _("Select a file to open"), self.conf["load_file_dir"],
                "json (*json)")
            self.open_file(file_name[0])

    def open_file_direct(self, file_name):
        """Returns a function that opens a specific file.

        Args:
            file_name (str): Path of the file to open.
        """
        def tmp():
            if self.save_maybe():
                self.open_file(file_name)
        return tmp

    def open_file(self, file_name):
        """Basic function to open a file.
        Args:
            file_name (str): Path of the file to open.
        """
        self.scene.clear()
        blocks = block_registry.Registry.load_block_structure(file_name)
        self.save_file_path = file_name
        self.conf["load_file_dir"] = file_name
        if file_name in self.conf["recent_files"]:
            self.conf["recent_files"].remove(file_name)
        self.conf["recent_files"] = [file_name] + self.conf["recent_files"][:3]
        self.update_recent_menu()
        self.scene.create_blocks(blocks)
        self.modified = False

    def update_recent_menu(self):
        """Updates the actions in the recent menu based on the last chosen
        files.
        """
        self.open_recent_menu.clear()
        for file_name in self.conf["recent_files"]:
            open_file_action = QtWidgets.QAction(
                ntpath.basename(file_name), self)
            open_file_action.triggered.connect(
                self.open_file_direct(file_name))
            self.open_recent_menu.addAction(open_file_action)

    def save_file_as(self):
        """Opens file dialog and save the current state to the given file.

        Returns:
            bool: True, if saving has been successful. False, otherwise.
        """
        file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, _("Save"), self.conf["save_file_dir"], "json (*.json)")
        if not file_name[0]:
            return False
        if not file_name[0].endswith(".json"):
            QtWidgets.QMessageBox.warning(
                self, _("Error"), _("File has to be a .json!"))
            return False
        else:
            self.save_file_path = file_name[0]
            self.conf["save_file_dir"] = os.path.dirname(self.save_file_path)
            self.save_file()

            self.conf["recent_files"] = [file_name[0]] + self.conf["recent_files"][:3]
            self.update_recent_menu()
            return True

    def save_file(self):
        """Saves the current state.

        Opens up a file dialog if no safe file has been specified yet.

        Returns:
            bool: True, if the file has been saved successfully.
                  Otherwise False.
        """
        if self.save_file_path:
            block_registry.Registry.save_block_structure(self.save_file_path)
            self.modified = False
            return True
        else:
            return self.save_file_as()

    def save_maybe(self):
        """Opens up a message dialogue asking if the user wants to save
        changes if the document has been modified.

        Returns:
            bool: True, if the action was accepted regardless
                  if the file was saved or not. False, if the action was
                  cancelled.
        """
        if self.modified:
            result = QtWidgets.QMessageBox.warning(
                self, _("Warning"),
                _("The document has been modified.\nDo you want to save your changes?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No)
        else:
            return True
        if result == QtWidgets.QMessageBox.Yes:
            return self.save_file()
        elif result == QtWidgets.QMessageBox.No:
            return True
        else:
            return False

    def clear(self):
        """Clears the :class:`.BlockScene` from all blocks."""
        result = QtWidgets.QMessageBox.question(
            self, _("Warning"),
            _("Are you sure you want to remove all blocks?"))
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            self.scene.clear()

    @property
    def modified(self):
        """Get or set whether there are any unsaved changes.

        Setting this property causes an update of the window title.
        """
        return self._modified

    @modified.setter
    def modified(self, value):
        self._modified = value
        if self.save_file_path:
            show_file = self.save_file_path
        else:
            show_file = _("untitled.json")
        if self._modified:
            show_file = "*" + show_file
        self.setWindowTitle("{} - {}".format(show_file, _("MCA")))


def change_language(new_language):
    """Change the language in the config.

    Args:
        new_language (str): New language which should be applied.
    """

    def tmp():
        config.Config()["language"] = new_language
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(_("Changes will be applied after restart."))
        msg_box.exec()

    return tmp
