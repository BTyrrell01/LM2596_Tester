#tests/hardware/test_psu_live.py

import pytest
import time

# Mark these tests as live hardware tests
pytestmark = pytest.mark.hardware_psu

# psu is the fixture name here.
def test_output_enable_disable(psu):
    # Turn output off, on, then off again
    psu.safe_state()
    psu.set_voltage_setpoint(1)
    time.sleep(1)
    
    psu.enable_output()
    time.sleep(1)
    
    psu.set_voltage_setpoint(0)
    psu.disable_output()

def test_idn_responds(psu):
    # print(psu.idn())
    assert psu.idn()

@pytest.mark.parametrize("bad_value", [-0.01, 30.01, 31])
def test_set_voltage_rejects_voltage_out_of_bounds_target(psu, bad_value):
    with pytest.raises(ValueError):
        psu.set_voltage_setpoint(31)

@pytest.mark.parametrize("bad_value", [True, "True", b"True", None])
def test_set_voltage_only_accepts_floats(psu, bad_value):
    with pytest.raises(TypeError):
        psu.set_voltage_setpoint(bad_value)

def test_set_voltage(psu):
    psu.set_voltage_setpoint(30)
    psu.set_voltage_setpoint(0)

def test_get_voltage(psu):
    psu.set_voltage_setpoint(30)
    psu.enable_output()
    time.sleep(1)
    
    assert psu.get_voltage() > 29.9 and psu.get_voltage() < 30.1
    psu.safe_state()

@pytest.mark.parametrize("bad_value", [True, "True", b"True", None])
def test_set_current_only_accepts_floats(psu, bad_value):
    with pytest.raises(TypeError):
        psu.set_output_current_setpoint(bad_value)

@pytest.mark.parametrize("bad_value", [-0.01, 5.1])
def test_set_current_rejects_current_out_of_bounds_target(psu, bad_value):
    with pytest.raises(ValueError):
        psu.set_output_current_setpoint(bad_value)

def test_set_current_setpoint(psu):
    psu.set_output_current_setpoint(1)

def test_set_beep(psu):
    psu.set_beep(False)
    psu.set_beep(True)
    psu.set_beep(False)

@pytest.mark.parametrize("bad_value", [0, 6])
def test_store_setting_rejects_out_of_bounds_numbers(psu, bad_value):
    with pytest.raises(ValueError):
        psu.store_setting(bad_value)

@pytest.mark.parametrize("bad_value", [True, "True", b"True", None])
def test_store_setting_accepts_only_ints(psu, bad_value):
    with pytest.raises(TypeError):
        psu.store_setting(bad_value)

def test_store_setting(psu):
    psu.store_setting(1)

@pytest.mark.parametrize("bad_value", [0, 6])
def test_recall_setting_rejects_out_of_bounds_numbers(psu, bad_value):
    with pytest.raises(ValueError):
        psu.store_setting(bad_value)

@pytest.mark.parametrize("bad_value", [True, "True", b"True", None])
def test_recall_setting_accepts_only_ints(psu, bad_value):
    with pytest.raises(TypeError):
        psu.recall_setting(bad_value)

def test_recall_setting(psu):
    psu.recall_setting(1)

def test_get_output_power(psu):
    psu.get_output_power()

@pytest.mark.parametrize("bad_value", ["True", 255, None])
def test_set_OCP_state_only_accepts_bool(psu, bad_value):
    with pytest.raises(TypeError):
        psu.set_OCP_state(bad_value)

@pytest.mark.parametrize("bad_value", [True, "True", b"True", None])
def test_set_OCP_threshold_only_accepts_float(psu, bad_value):
    with pytest.raises(TypeError):
        psu.set_OCP_threshold(bad_value)

@pytest.mark.parametrize("bad_value", [1000, 5.01, -1, -0.01])
def test_set_OCP_threshold_out_of_bounds(psu, bad_value):
    with pytest.raises(ValueError):
        psu.set_OCP_threshold(bad_value)

def test_set_OCP_threshold(psu):
    psu.set_OCP_threshold(5)

def test_set_OCP_state(psu):
    psu.set_OCP_state(True)
    psu.set_OCP_state(False)

@pytest.mark.parametrize("bad_value", ["True", 255, None])
def test_set_OVP_state_only_accepts_bool(psu, bad_value):
    with pytest.raises(TypeError):
        psu.set_OVP_state(bad_value)

@pytest.mark.parametrize("bad_value", [1000, 30.01, -1, -0.01])
def test_set_OVP_threshold_out_of_bounds(psu, bad_value):
    with pytest.raises(ValueError):
        psu.set_OVP_threshold(bad_value)

def test_set_OVP_threshold(psu):
    psu.set_OVP_threshold(30)

def test_set_OVP_state(psu):
    psu.set_OVP_state(True)
    psu.set_OVP_state(False)

