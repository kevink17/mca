from scipy.signal import stft

from mca.framework import validator, parameters, data_types, PlotBlock
from mca.language import _


class STFTPlot(PlotBlock):
    """Plots the Short-Time Fourier Transformation of the input signal."""
    name = _("STFTPlot")
    description = _("Plots the Short-Time Fourier Transformation of the "
                    "input signal.")
    tags = (_("Plotting"), _("Fouriertransformation"))

    def __init__(self, **kwargs):
        """Initializes STFTPlot class."""
        super().__init__(rows=1, cols=1, **kwargs)
        self.color_bar = None

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "window": parameters.ChoiceParameter(
                name=_("Window"),
                choices=[
                    ("boxcar", _("Rectangle")),
                    ("hann", _("Hann")),
                    ("hamming", _("Hamming")),
                    ("triangle", _("Triangle"))],
                default="hann"),
            "seg_length": parameters.IntParameter(
                name=_("Segment Length"), min_=1, default=20),
            "seg_overlap": parameters.IntParameter(
                name=_("Segment Overlap"), min_=0, default=10),
            "fft_length": parameters.IntParameter(
                name=_("FFT Length"), min_=1, default=20),
        })

    def setup_plot_parameters(self):
        self.plot_parameters["cmap"] = parameters.ChoiceParameter(
            name=_("Colormap"),
            choices=(("viridis", _("Viridis")),
                     ("plasma", _("Plasma")),
                     ("inferno", _("Inferno")),
                     ("magma", _("Magma")),
                     ("cividis", _("Cividis"))
                     ),
            default="viridis"
        )

    def _process(self):
        if self.color_bar:
            self.color_bar.remove()
            self.color_bar = None
        self.axes.cla()
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return

        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data

        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value
        cmap = self.plot_parameters["cmap"].value

        f, t, z = stft(x=input_signal.ordinate, fs=1 / input_signal.increment,
                       window=window, nperseg=seg_length, noverlap=seg_overlap,
                       nfft=fft_length)
        im = self.axes.pcolormesh(t, f, abs(z), cmap=cmap)
        self.color_bar = self.fig.colorbar(im, ax=self.axes)
        metadata = data_types.MetaData(self.inputs[0].metadata.name,
                                       unit_a=self.inputs[0].metadata.unit_a,
                                       unit_o=1 / self.inputs[0].metadata.unit_a)
        abscissa_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_a,
            unit=metadata.unit_a,
            symbol=metadata.symbol_a
        )
        ordinate_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_o,
            unit=metadata.unit_o,
            symbol=metadata.symbol_o
        )
        self.axes.set_xlabel(abscissa_string)
        self.axes.set_ylabel(ordinate_string)

        self.axes.grid(True)

        self.fig.canvas.draw()
