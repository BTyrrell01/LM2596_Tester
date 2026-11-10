# driver for Korad KA3005P power supply
from enum import Enum, IntFlag

class Status(IntFlag):
    CH1_CONSTANT_VOLTAGE = 1 << 0
    CH2_CONSTANT_VOLTAGE = 1 << 1
    TRACKING = 3 << 2
    BEEP_ON = 1 << 4
    OCP_ON = 1 << 5
    OUTPUT_ON = 1 << 6
    OVP_ON = 1 << 7

class OutputMode(Enum):
    CONSTANT_CURRENT = "CC"
    CONSTANT_VOLTAGE = "CV"

class ProtectionEnabled(Enum):
    OVERCURRENT = "OCP"
    OVERVOLTAGE = "OCV"

class Ka3005p:
    MAX_VOLTAGE = 30    # From the datasheet
    MIN_VOLTAGE = 0

    def __init__(self, resource, timeout=5000):
        self._resource = resource
        self._resource.timeout = timeout    # Timeout in ms
        self._resource.baud_rate = 9600
        self._resource.read_termination = "\n"
        self._resource.write_termination = "\n"

    def _status(self) -> Status:
        # Write to the psu then read raw bytes instead of trying to decode the readback values
        self._resource.write("STATUS?")
        raw = self._resource.read_bytes(2)
        
        return Status(int.from_bytes(raw[:1], "big"))

    def _check_valid_channel(self, channel) -> bool:
        if channel < 1 or channel > 2:
            raise ValueError(f"Invalid channel {channel}")

    def idn(self) -> str:
        return self._resource.query("*IDN?")

    def safe_state(self):
        self.disable_output()

    def enable_output(self):
        self._resource.write("OUT1")

        # Check that the output is now enabled
        if self.output_state() == False:
            raise RuntimeError(f"Expected output enabled, output is disabled")

    def disable_output(self):
        self._resource.write("OUT0")

        # Check that the output is now disabled
        if self.output_state() == True:
            raise RuntimeError(f"Expected output disabled, output is enabled")
    
    def output_state(self) -> bool:
        if Status.OUTPUT_ON in self._status():
            return True
        return False

    def get_voltage(self, channel: int) -> float:
        self._check_valid_channel(channel)
        return float(self._resource.query(f"VOUT{channel}?"))

    def get_voltage_setpoint(self, channel: int) -> float:
        self._check_valid_channel(channel)
        return float(self._resource.query(f"VSET{channel}?"))

    def set_voltage_setpoint(self, channel: int, target_voltage: float):
        self._check_valid_channel(channel)

        if target_voltage < self.MIN_VOLTAGE or target_voltage > self.MAX_VOLTAGE:
            raise ValueError(f"Voltage outside allowed range of 0 - 30")


        # Write to the supply
        self._resource.write(f"VSET{channel}:{target_voltage}")
        
        # Check the value is correct
        new_voltage = self.get_voltage_setpoint(channel)

        if abs(new_voltage - target_voltage) > 0.1:
            raise RuntimeError(f"Voltage setpoint is {new_voltage} V, expected {target_voltage} V")

    def get_output_mode(self, channel: int) -> OutputMode:
        self._check_valid_channel(channel)
 
        # There are 2 channels, ensure that we only use those 2
        if channel == 1:
            flag = Status.CH1_CONSTANT_VOLTAGE
        else:
            flag = Status.CH2_CONSTANT_VOLTAGE

        if flag in self._status():
            return OutputMode.CONSTANT_VOLTAGE
        return OutputMode.CONSTANT_CURRENT

    def set_output_current_setpoint(self, channel: int, target_current: float):
        self._check_valid_channel(channel)
        
        # Check that the target current is within bounds
        if target_current < 0 or target_current > 5:
            raise ValueError(f"Target current {target_current} outside of range 0-5A")
        
        self._resource.write(f"ISET{channel}:{target_current}")

        # Check that the target current moved to the target
        new_current_setpoint = self.get_output_current_setpoint(channel)

        if abs(new_current_setpoint - target_current) > 0.01:
            raise RuntimeError(f"Current setpoint is {new_current_setpoint} A, expected {target_current} A")

    def get_output_current_setpoint(self, channel: int) -> float:
        self._check_valid_channel(channel)
        return float(self._resource.query(f"ISET{channel}?"))
