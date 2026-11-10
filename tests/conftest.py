# tests/hardware/conftest.py
# Make the fixture for the hardware tests

import os
import pytest
import pyvisa
from embedded_test_suite.drivers.ka3005p import Ka3005p

def pytest_addoption(parser):
    parser.addoption(
            "--psu-addr",
            default=os.environ.get("PSU_ADDR"),
            help="VISA resource string for the power supply, set PSU_ADDR"
            )

# Separate fixture so that no matter if setup fails halfway we don't leak resources.
@pytest.fixture(scope="session")
def rm():
    rm = pyvisa.ResourceManager()
    yield rm
    rm.close()


@pytest.fixture(scope="session")
def psu(request, rm):
    addr = request.config.getoption("--psu-addr")
    
    if not addr:
        pytest.skip("PSU_ADDR is empty or not provided")

    try:
        inst = rm.open_resource(addr)
    except pyvisa.errors.VisaIOError as e:
        pytest.fail(f"Could not open {addr}: {e}", pytrace=False)

    # If we can't put the power supply in a safe state then cleanup.
    try:
        supply = Ka3005p(inst, timeout=5000)
        supply.safe_state()     # Put the psu in a safe state before handing it off
        yield supply
    finally:
        try:
            supply.safe_state()
        finally:
            inst.close()
