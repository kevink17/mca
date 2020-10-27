import copy

from mca.framework import validator, data_types, Block
from mca.language import _


class RealImag(Block):
    """Block class which separates the real and imaginary part of the input
    signal in two output signals.

    This block has one input and two outputs. First output has the real part
    and second output has the imaginary part.
    """
    name = _("RealImagBlock")
    description = _("Divides the real and imaginary part of "
                    "the input signal into two output signals.")
    tags = (_("Processing"),)

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            name=_("Real part")
        )
        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            name=_("Imaginary part")
        )
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        validator.check_type_signal(self.inputs[0].data)
        real_signal = copy.copy(self.inputs[0].data)
        real_signal.ordinate = real_signal.ordinate.real
        imag_signal = copy.copy(self.inputs[0].data)
        imag_signal.ordinate = imag_signal.ordinate.imag
        self.outputs[0].data = real_signal
        self.outputs[0].data.meta_data = self.outputs[0].get_meta_data(
            real_signal.meta_data)
        self.outputs[1].data = imag_signal
        self.outputs[1].data.meta_data = self.outputs[1].get_meta_data(
            imag_signal.meta_data)
