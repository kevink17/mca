import pytest
from mca.block import absolute
from mca.base import block_base
from mca.datatypes import signal
import numpy as np
import test_data


@pytest.mark.parametrize("test_input", [-5, 1, np.arange(-1, 10)])
def test_absolute_basic(test_input):
    a = absolute.Absolute()
    b = test_data.TestBlock(signal.Signal(None, None, None, None, test_input))
    a.inputs[0].connect(b.outputs[0])
    if isinstance(test_input, int):
        assert a.outputs[0].data.ordinate >= 0
    if isinstance(test_input, np.ndarray):
        assert all(x >= 0 for x in a.outputs[0].data.ordinate)
