#tests/hardware/test_scope_live.py
from embedded_test_suite.drivers.sds822x import Measurement
import pytest
import time

# Mark these tests as live hardware tests
pytestmark = pytest.mark.hardware_scope

# sds822x is the fixture
def test_idn_responds(sds822x):
    assert sds822x.idn()

def test_set_measurement_state(sds822x):
    sds822x.set_measurement_state(False)
    sds822x.set_measurement_state(True)
    sds822x.set_measurement_state(False)

@pytest.mark.parametrize("good_value", [Measurement.MAX, Measurement.MEAN, Measurement.FREQ])
def test_set_measurement_type(sds822x, good_value):
    sds822x.set_measurement_state(True)
    sds822x.set_measurement_type(good_value, 1)
    sds822x.set_measurement_type(good_value, 2)

def test_auto_set(sds822x):
    sds822x.auto_set()

