import json
import random
import pathlib

from PySide6 import QtWidgets, QtCore, QtGui

from mca.framework import load, save
from mca.gui.pyside6 import block_item
from mca.language import _


class BlockView(QtWidgets.QGraphicsView):
    """Class for visualizing the blocks in the connected :class:`.BlockScene`.
    Manages how blocks are displayed like deciding which :class:`.BlockItem`
    or `.ConnectionLine` is painted over other colliding items.
    """

    def __init__(self, scene, parent):
        """Initialize BlockView class.

        Args:
            scene: Scene belonging to this view which holds the items to
                   display.
            parent: Parent of this widget.
        """
        QtWidgets.QGraphicsView.__init__(self, scene=scene, parent=parent)
        self.setMinimumSize(500, 400)
        self.zoom_factor = 1
        # Relative path for the toolbar icons
        gui_path = pathlib.Path(__file__).parent
        icon_path = gui_path / "../../resources/icons/"
        # Define actions
        self.zoom_in_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "magnifying-glass-plus.png")),
            _("Zoom in"))
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_in_action.setToolTip(
            "{}, {}".format(_("Zoom in"), _("Ctrl +")))
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "magnifying-glass-minus.png")),
            _("Zoom out")
        )
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_out_action.setToolTip("{}, {}".format(_("Zoom out"),
                                                        _("Ctrl -")))
        self.addAction(self.zoom_out_action)

        self.zoom_original_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "increase.png")), _("Zoom original")
        )
        self.zoom_original_action.triggered.connect(self.zoom_original)

        self.copy_action = QtGui.QAction(QtGui.QIcon(
            str(icon_path / "copy.png")), _("Copy")
        )
        self.copy_action.triggered.connect(self.scene().copy_selected)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setToolTip("{}, {}".format(_("Copy"), _("Ctrl+C")))

        self.paste_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "paste.png")), _("Paste")
        )
        self.paste_action.triggered.connect(self.scene().paste_selected)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setToolTip("{}, {}".format(_("Paste"), "Ctrl+V"))

        self.cut_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "cut-with-scissors.png")), _("Cut")
        )
        self.cut_action.triggered.connect(self.scene().cut_selected)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setToolTip("{}, {}".format(_("Cut"), _("Ctrl+X")))

        self.delete_action = QtGui.QAction(
            QtGui.QIcon(str(icon_path / "bin.png")), _("Delete"))
        self.delete_action.triggered.connect(self.scene().delete_selected)
        self.delete_action.setShortcut("Del")
        self.delete_action.setToolTip("{}, {}".format(_("Delete"), _("Del")))
        self.clear_action = QtGui.QAction(QtGui.QIcon(
            str(icon_path / "archeology.png")), _("Clear")
        )
        self.clear_action.triggered.connect(self.scene().clear)

        self.setBackgroundBrush(draw_pattern(40, QtGui.Qt.gray))
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        self.default_context_menu = QtWidgets.QMenu(self)
        self.default_context_menu.addAction(self.paste_action)

        self.selection_context_menu = QtWidgets.QMenu(self)
        self.selection_context_menu.addAction(self.copy_action)
        self.selection_context_menu.addAction(self.paste_action)
        self.selection_context_menu.addAction(self.cut_action)
        self.selection_context_menu.addAction(self.delete_action)

    def zoom_in(self):
        """Zooms in by scaling the size of all items up."""
        self.scale(1.2, 1.2)
        self.zoom_factor *= 1.2

    def zoom_out(self):
        """Zooms out by scaling the size of all items down."""
        self.scale(1 / 1.2, 1 / 1.2)
        self.zoom_factor /= 1.2

    def zoom_original(self):
        """Zooms to the original scale."""
        self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        self.zoom_factor = 1

    def mousePressEvent(self, event):
        """Method invoked when a mouse button has been pressed."""
        if event.button() == QtGui.Qt.MiddleButton:
            self.setDragMode(self.ScrollHandDrag)
            new_event = QtGui.QMouseEvent(
                QtCore.QEvent.GraphicsSceneMousePress,
                event.pos(), QtGui.Qt.MouseButton.LeftButton,
                event.buttons(),
                QtGui.Qt.KeyboardModifier.NoModifier)
            self.mousePressEvent(new_event)
        if event.button() == QtGui.Qt.RightButton:
            if self.scene().selectedItems() and not self.itemAt(event.pos()):
                self.selection_context_menu.exec_(event.screenPos().toPoint())
            elif not self.itemAt(event.pos()):
                self.default_context_menu.exec_(event.screenPos().toPoint())
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Method invoked when a mouse button has been released."""
        if event.button() == QtGui.Qt.MiddleButton:
            new_event = QtGui.QMouseEvent(
                QtCore.QEvent.GraphicsSceneMouseRelease,
                event.pos(), QtGui.Qt.MouseButton.LeftButton,
                event.buttons(),
                QtGui.Qt.KeyboardModifier.NoModifier)
            self.mouseReleaseEvent(new_event)
            self.setDragMode(self.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Method invoked when the mouse wheel is used."""
        if event.modifiers() == QtCore.Qt.CTRL:
            if event.delta() > 0:
                self.zoom_in_action.trigger()
            else:
                self.zoom_out_action.trigger()


class BlockScene(QtWidgets.QGraphicsScene):
    """Main class for basic operations with graphic items. This class manages
    for example adding items, finding items or removing items from itself.

    Attributes:
        block_list: Reference of the widget that holds all block classes.
    """

    def __init__(self, parent):
        """Initializes BlockScene class.

        Args:
            parent: Parent of this widget.
        """
        QtWidgets.QGraphicsScene.__init__(self, parent=parent)
        self.block_list = None

    def dragEnterEvent(self, event):
        """Method invoked when a drag enters this widget. Accepts only
        events that were created from the :class:`.BlockList`.
        """
        if event.source() is self.block_list:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Method invoked when a drag moves in this widget."""
        event.accept()

    def dropEvent(self, event):
        """Method invoked when a drag gets dropped in this widget.
        Creates a block and adds it to the scene if source of the event was
        from an item of the :class:`.BlockList`.
        """
        event.accept()
        event.setDropAction(QtCore.Qt.CopyAction)
        pos = (event.scenePos().x(), event.scenePos().y())
        block_class = event.source().selectedItems()[0].data(3)
        self.create_block_item(block_class(), pos=pos, open_edit_window=False)

    def clear(self):
        """Removes all items from the BlockScene."""
        for item in self.items():
            if isinstance(item, block_item.BlockItem):
                item.delete()

    def create_block_item(self, block, pos=None, width=100, height=100,
                          open_edit_window=False):
        """Creates a new :class:`.BlockItem` to an existing :class:`.Block`.

        Args:

            block: :class:`.Block` instance the block item represents.
            pos (tuple): (x,y) - Position of the block. If set to None a
                         pseudo random position will be calculated based on
                         the position of current blocks in the scene.
            width (int): Width of the BlockItem.
            height (int): Width of the BlockItem.
            open_edit_window (bool): True, if the edit window
                                     should be opened immediately after
                                     initializing the block.

        """
        if pos is None:
            # Compute the average position of the blocks
            avg_x, avg_y = 0, 0
            for item in self.items():
                avg_x += item.scenePos().x()
                avg_y += item.scenePos().y()
            if len(self.items()) > 0:
                avg_x = avg_x / len(self.items())
                avg_y = avg_y / len(self.items())
            # Add some noise to the coordinates
            x = avg_x + random.randint(-100, 100)
            y = avg_y + random.randint(-100, 100)
        else:
            x = pos[0]
            y = pos[1]

        new_block = block_item.BlockItem(self.views()[0], block,
                                         x=x,
                                         y=y,
                                         block_width=width,
                                         block_height=height)

        self.addItem(new_block)
        if open_edit_window:
            new_block.open_edit_window()
        self.parent().parent().modified = True

    def create_blocks(self, blocks):
        """Create the graphical :class:`.BlockItem` structure of an existing
        :class:`.Block` structure.

        Args:
            blocks (list): Existing block structure to represent.
        """
        # Create the block items from the blocks
        for block in blocks:
            if block.gui_data["save_data"].get("pyside6"):
                pos = block.gui_data["save_data"]["pyside6"]["pos"]
                width = block.gui_data["save_data"]["pyside6"]["size"][0]
                height = block.gui_data["save_data"]["pyside6"]["size"][1]
            else:
                pos = (0, 0)
                width = 100
                height = 100
            self.create_block_item(block=block, pos=pos, width=width,
                                   height=height, open_edit_window=False)
        # Set the runtime data and connect inputs and outputs in the gui
        for block in blocks:
            for input_index, input_ in enumerate(block.inputs):
                if input_.connected_output:
                    output = input_.connected_output
                    block_item = block.gui_data["run_time_data"]["pyside6"][
                        "block_item"]
                    input_item = block_item.inputs[input_index]
                    block_item = \
                    output.block.gui_data["run_time_data"]["pyside6"][
                        "block_item"]
                    output_item = block_item.outputs[
                        output.block.outputs.index(output)]
                    input_item.connect(output_item, loading=True)

    def copy_selected(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard.
        """
        # Get the clipboard object
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()

        if self.selectedItems():
            mime_data = QtCore.QMimeData()
            # Get the backend blocks of the selscted gui blocks
            backend_blocks = [block.block for block in self.selectedItems()]
            # Compute the relative positions of the blocks
            x_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                    0], backend_blocks))
            y_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                    1], backend_blocks))
            for block in backend_blocks:
                block.gui_data["save_data"]["pyside6"]["pos"][0] -= x_min
                block.gui_data["save_data"]["pyside6"]["pos"][1] -= y_min
            # Get the json representation from the blocks
            json_blocks = save.blocks_to_json(backend_blocks)
            # Set the clipboard data
            mime_data.setText(json_blocks)
            clipboard.setMimeData(mime_data)
        else:
            clipboard.clear()

    def paste_selected(self):
        """Pastes copied blocks from the clipboard into the scene."""
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()
        if not clipboard.mimeData().text():
            return
        # Check if clipboard has json string
        try:
            pasted_blocks = load.json_to_blocks(clipboard.mimeData().text())
        except json.decoder.JSONDecodeError:
            return
        # Map global mouse pos to view pos
        global_pos = QtGui.QCursor.pos()
        view_pos = self.views()[0].mapFromGlobal(global_pos)
        view_size = self.views()[0].size()
        # Check if mouse is within view
        if (view_pos.x() >= 0) & (view_pos.y() >= 0) & (
                view_pos.x() <= view_size.width()) & (
                view_pos.y() <= view_size.height()):
            scene_pos = self.views()[0].mapToScene(view_pos)
            # Paste all block centered to the mouse
            x_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                    0], pasted_blocks))
            y_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                    1], pasted_blocks))
            x_max = max(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                                      0] +
                                  block.gui_data["save_data"]["pyside6"][
                                      "size"][0], pasted_blocks))
            y_max = max(
                map(lambda block: block.gui_data["save_data"]["pyside6"]["pos"][
                                      1] +
                                  block.gui_data["save_data"]["pyside6"][
                                      "size"][1], pasted_blocks))
            paste_width = x_max - x_min
            paste_height = y_max - y_min
            for block in pasted_blocks:
                block.gui_data["save_data"]["pyside6"]["pos"][
                    0] += scene_pos.x() - paste_width // 2
                block.gui_data["save_data"]["pyside6"]["pos"][
                    1] += scene_pos.y() - paste_height // 2
        self.create_blocks(pasted_blocks)

    def cut_selected(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard. Deletes the selected block afterwards.
        """
        self.copy_selected()
        self.delete_selected()

    def delete_selected(self):
        """Deletes the selected block from the scene."""
        for item in self.selectedItems():
            if isinstance(item, block_item.BlockItem):
                item.delete()


def draw_pattern(step, color):
    """Draws the background pattern of the block view."""
    pixmap = QtGui.QPixmap(step, step)
    pixmap.fill(QtGui.Qt.transparent)
    painter = QtGui.QPainter()
    painter.begin(pixmap)
    painter.setPen(color)
    width = step - 1
    painter.drawLine(0, 0, 2, 0)
    painter.drawLine(0, 0, 0, 2)
    painter.drawLine(0, width - 1, 0, width)
    painter.drawLine(width - 1, 0, width, 0)
    return pixmap
