from scipy.signal import hilbert

from mca.framework import Block, data_types, util


class AnalyticalSignal(Block):
    """Computes the analytical signal of the input signal."""
    name = "Analytical Signal"
    description = "Computes the analytical signal of the input signal using the Hilbert transform."
    tags = ("Processing",)
    references = {"scipy.signal.hilbert":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.hilbert.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        pass

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Calculate the ordinate
        analytical_signal = hilbert(input_signal.ordinate)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=analytical_signal,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
