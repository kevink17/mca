import copy

from mca.framework import Block, util
from mca.language import _


class ComplexToReal(Block):
    """Separates the real and imaginary part of the input
    signal in two signals.

    First output yields the real part and second output yields the imaginary
    part.
    """
    name = _("ComplexToReal")
    description = _("Separates the real and imaginary part of "
                    "the input signal into two output signals. First output "
                    "yields the real part and second output yields the "
                    "imaginary part.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(name=_("Real part"))
        self.new_output(name=_("Imaginary part"))
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        # Read the input data
        real_signal = copy.copy(self.inputs[0].data)
        imag_signal = copy.copy(self.inputs[0].data)
        # Calculate the ordinates
        real_signal.ordinate = real_signal.ordinate.real
        imag_signal.ordinate = imag_signal.ordinate.imag
        # Apply new signal to the outputs
        self.outputs[0].data = real_signal
        self.outputs[1].data = imag_signal
        # Apply metadata from the input to the outputs
        self.outputs[0].process_metadata = self.inputs[0].metadata
        self.outputs[1].process_metadata = self.inputs[0].metadata
