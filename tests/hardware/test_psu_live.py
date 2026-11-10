#tests/hardware/test_psu_live.py

import pytest
import time

# Mark these tests as live hardware tests
pytestmark = pytest.mark.hardware

# psu is the fixture name here.
def test_output_enable_disable(psu):
    # Turn output off, on, then off again
    psu.safe_state()
    psu.set_voltage_setpoint(1, 1)
    time.sleep(1)
    
    psu.enable_output()
    time.sleep(1)
    
    psu.set_voltage_setpoint(1, 0)
    psu.disable_output()

def test_idn_responds(psu):
    # print(psu.idn())
    assert psu.idn()

def test_set_voltage_rejects_too_high(psu):
    with pytest.raises(ValueError):
        psu.set_voltage_setpoint(1, 31)

def test_set_voltage_rejects_too_low(psu):
    with pytest.raises(ValueError):
        psu.set_voltage_setpoint(1, -1)

def test_set_voltage_rejects_channel_too_high(psu):
    with pytest.raises(ValueError):
        psu.set_voltage_setpoint(3, 12)

def test_set_voltage_rejects_channel_too_low(psu):
    with pytest.raises(ValueError):
        psu.set_voltage_setpoint(0, 12)

def test_set_voltage(psu):
    psu.set_voltage_setpoint(1, 30)
    psu.set_voltage_setpoint(1, 0)

def test_get_voltage(psu):
    psu.set_voltage_setpoint(1, 30)
    psu.enable_output()
    time.sleep(1)
    breakpoint()
    assert psu.get_voltage(1) > 29.9 and psu.get_voltage(1) < 30.1
    psu.safe_state()

def test_set_current_rejects_channel_too_high(psu):
    with pytest.raises(ValueError):
        psu.set_output_current(3, 1)
        psu.safe_state()

def test_set_current_rejects_channel_too_low(psu):
    with pytest.raises(ValueError):
        psu.set_output_current(-1, 1)
        psu.safe_state()

def test_set_current_rejects_current_setpoint_too_high(psu):
    with pytest.raises(ValueError):
        psu.set_output_current(1, 5.1)
        psu.safe_state()

def test_set_current_rejects_current_setpoint_too_low(psu):
    with pytest.raises(ValueError):
        psu.set_output_current(1, -0.1)
        psu.safe_state()

def test_set_current(psu):
    psu.set_voltage_setpoint(1, 1)
    psu.set_output_current(1, 0.5)
    time.sleep(1)

    psu.get_output_current(1)
