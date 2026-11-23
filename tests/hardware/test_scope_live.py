#tests/hardware/test_scope_live.py

import pytest
import time

# Mark these tests as live hardware tests
pytestmark = pytest.mark.hardware_scope

# sds822x is the fixture
def test_idn_responds(sds822x):
    assert sds822x.idn()
