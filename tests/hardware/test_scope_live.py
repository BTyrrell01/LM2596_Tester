#tests/hardware/test_scope_live.py
from embedded_test_suite.drivers.sds822x import Measurement
import pytest
import time

# Mark these tests as live hardware tests
pytestmark = pytest.mark.hardware_scope

# sds822x is the fixture
def test_idn_responds(sds822x):
    assert sds822x.idn()

def test_auto_set(sds822x):
    sds822x.auto_set()

def test_get_measurement_value(sds822x):
    sds822x.auto_set()

    assert sds822x.get_measurement_value(Measurement.FREQ, 1) == pytest.approx(1000, rel=0.01)


