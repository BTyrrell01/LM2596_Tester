# tests/hardware/conftest.py
# Make the fixture for the hardware tests

import os
import pytest
import pyvisa
from embedded_test_suite.drivers.ka3005p import Ka3005p
from embedded_test_suite.drivers.sds822x import Sds822x

def pytest_addoption(parser):
    parser.addoption(
            "--psu-addr",
            default=os.environ.get("PSU_ADDR"),
            help="VISA resource string for the power supply, set PSU_ADDR"
            )

    parser.addoption(
            "--scope-addr",
            default=os.environ.get("SCOPE_ADDR"),
            help="SDS822X IP ADDR"
            )

# Separate fixture so that no matter if setup fails halfway we don't leak resources.
@pytest.fixture(scope="session")
def rm_py():
    rm = pyvisa.ResourceManager("@py")
    yield rm
    rm.close()

@pytest.fixture(scope="session")
def tm_ivi():
    rm = pyvisa.ResourceManager("@ivi")
    yield rm
    rm.close()

@pytest.fixture(scope="session")
def psu(request, rm_py):
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

@pytest.fixture(scope="session")
def sds822x(request, rm_ivi):
    addr = request.config.getoption("--scope-addr")

    if not addr:
        pytest.skip("SCOPE_ADDR is empty or not provided")

    try:
        inst = rm.open_resource(f"TCPIP0::{addr}::inst0::INSTR")
    except pyvisa.errors.VisaIOError as e:
        pytest.fail(f"Could not open {addr}: {e}", pytrace=False)

    # If we can't put the scope in the default state then cleanup.
    try:
        scope = Sds822x(inst, timeout=5000)
        scope.default_state()
        yield scope
    finally:
        inst.close()


