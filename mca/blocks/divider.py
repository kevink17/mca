from mca.framework import validator, data_types, Block, helpers
from mca.language import _


class Divider(Block):
    """Divides the two input signals."""
    name = _("Divider")
    description = _("Divides the two input signals.")
    tags = (_("Processing"),)

    def setup_io(self):
        self._new_output(
            meta_data=data_types.default_meta_data())
        self._new_input()
        self._new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.check_any_empty_inputs():
            return
        for i in self.inputs:
            validator.check_type_signal(i.data)
        input_signals = [self.inputs[0].data, self.inputs[1].data]
        abscissa_units = [signal.meta_data.unit_a for signal in input_signals]
        validator.check_same_units(abscissa_units)
        validator.check_intervals(input_signals)
        matched_signals = helpers.fill_zeros(input_signals)
        ordinate = input_signals[0].ordinate/input_signals[1].ordinate
        unit_a = matched_signals[0].meta_data.unit_a
        unit_o = input_signals[0].meta_data.unit_o / input_signals[1].meta_data.unit_o
        meta_data = data_types.MetaData(None, unit_a, unit_o)
        abscissa_start = matched_signals[0].abscissa_start
        values = matched_signals[0].values
        increment = matched_signals[0].increment
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].get_meta_data(meta_data),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
