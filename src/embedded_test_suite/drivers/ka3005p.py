# driver for Korad KA3005P power supply
from enum import Enum, IntFlag
from pyvisa.constants import StopBits, Parity
import pyvisa
import time

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

class Ka3005p:
    MAX_VOLTAGE = 30    # From the datasheet
    MIN_VOLTAGE = 0
    MAX_CURRENT = 5
    MIN_CURRENT = 0
    MEMORY_CHANNELS = range(1, 6)
    _CH = 1     # There is only 1 channel on this PSU model

    def __init__(self, resource, timeout=5000):
        self._resource = resource
        self._resource.timeout = timeout    # Timeout in ms
        self._resource.baud_rate = 9600
        self._resource.data_bits = 8
        self._resource.stop_bits = StopBits.one
        self._resource.parity = Parity.none
        #self._resource.read_termination = "\n"     # It seems that the KA3005P doesn't know how to handle these
        #self._resource.write_termination = "\n"

    def _status(self) -> Status:
        # Drain the buffer because of rough firmware
        self._drain_buffer()

        # Write to the psu then read raw bytes instead of trying to decode the readback values
        self._resource.write("STATUS?")
        raw = self._resource.read_bytes(2)
        
        return Status(int.from_bytes(raw[:1], "big"))

    def _as_float(self, value, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        return float(value)

    def _as_int(self, value, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        return int(value)

    def _drain_buffer(self) -> None:
        original_timeout = self._resource.timeout
        self._resource.timeout = 100  # Set a short 100 ms timeout
        
        try:
            # Read until buffer is empty
            while True:
                self._resource.read_raw()
        except pyvisa.VisaIOError:
            pass  # Buffer is now empty
        finally:
            # Restore the original timeout
            self._resource.timeout = original_timeout

    def idn(self) -> str:
        return self._resource.query("*IDN?")

    def safe_state(self) -> None:
        self.disable_output()

    def enable_output(self) -> None:
        self._resource.write("OUT1")

        # Check that the output is now enabled
        if self.output_state() == False:
            raise RuntimeError(f"Expected output enabled, output is disabled")

    def disable_output(self) -> None:
        self._resource.write("OUT0")

        # Check that the output is now disabled
        if self.output_state() == True:
            raise RuntimeError(f"Expected output disabled, output is enabled")
    
    def output_state(self) -> bool:
        if Status.OUTPUT_ON in self._status():
            return True
        return False

    def get_voltage(self) -> float:
        return float(self._resource.query(f"VOUT{self._CH}?"))

    def get_voltage_setpoint(self) -> float:
        return float(self._resource.query(f"VSET{self._CH}?"))

    def set_voltage_setpoint(self, target_voltage: float) -> None:
        # Make sure the user passed in a float
        target_voltage = self._as_float(target_voltage, "target_voltage")

        if target_voltage < self.MIN_VOLTAGE or target_voltage > self.MAX_VOLTAGE:
            raise ValueError(f"Voltage outside allowed range of 0 - 30")

        # Write to the supply
        self._resource.write(f"VSET{self._CH}:{target_voltage}")
        
        # Check the value is correct
        new_voltage = self.get_voltage_setpoint()

        if abs(new_voltage - target_voltage) > 0.1:
            raise RuntimeError(f"Voltage setpoint is {new_voltage} V, expected {target_voltage} V")

    def get_output_mode(self) -> OutputMode: 
        # Check if we're in CV or CC mode
        if Status.CH1_CONSTANT_VOLTAGE in self._status():
            return OutputMode.CONSTANT_VOLTAGE
        return OutputMode.CONSTANT_CURRENT

    def set_output_current_setpoint(self, target_current: float) -> None:
        
        # Ensure that we are using a float for future arguments
        target_current = self._as_float(target_current, "target_current")

        # Check that the target current is within bounds
        if target_current < self.MIN_CURRENT or target_current > self.MAX_CURRENT:
            raise ValueError(f"Target current {target_current} outside of range 0-5A")
        
        self._resource.write(f"ISET{self._CH}:{target_current}")

        # Check that the target current setpoint moved to the target
        new_current_setpoint = self.get_output_current_setpoint()

        if abs(new_current_setpoint - target_current) > 0.01:
            raise RuntimeError(f"Current setpoint is {new_current_setpoint} A, expected {target_current} A")

    def get_output_current_setpoint(self) -> float:
        return float(self._resource.query(f"ISET{self._CH}?"))

    def set_beep(self, state: bool) -> None:
        
        # Make sure the user passed in a bool
        if not isinstance(state, bool):
            raise TypeError(f"State must be a bool, got {type(state).__name__}")

        self._resource.write(f"BEEP{int(state)}")

        hw_beep_state = Status.BEEP_ON in self._status()

        # Check that we actually set the beep
        if hw_beep_state != state:
            raise RuntimeError(
                    f"Beep is {'ON' if hw_beep_state else 'OFF'}, "
                    f"Expected {'ON' if state else 'OFF'}"
            )

    def recall_setting(self, setting: int) -> None:

        # Make sure the user passed in an int from 1 - 5
        setting = self._as_int(setting, "setting")

        if setting not in self.MEMORY_CHANNELS:
            raise ValueError(f"Setting {setting} is invalid, must be one of {list(self.MEMORY_CHANNELS)}")
        
        self._resource.write(f"RCL{setting}") 
        # Not quite sure how we would verify that the setting is what we wanted it to be

    def store_setting(self, setting: int) -> None:

        # Make sure the user passed in a valid int
        setting = self._as_int(setting, "setting")

        if setting not in self.MEMORY_CHANNELS:
            raise ValueError(f"Setting {setting} is invalid, must be one of {list(self.MEMORY_CHANNELS)}")
        
        self._resource.write(f"SAV{setting}")
        
        # Not quite sure how we would verify that the setting actually worked yet

    def set_OCP_state(self, state: bool) -> None:
        # Make sure the user passed in a bool
        if not isinstance(state, bool):
            raise TypeError(f"State must be a bool, got {type(state).__name__}")

        self._resource.write(f"OCP{int(state)}")

        # Check to make sure that the state what we expect
        hw_OCP_state = Status.OCP_ON in self._status()

        if hw_OCP_state != state:
            raise RuntimeError(
                    f"OCP is {'ON' if hw_OCP_state else 'OFF'}, "
                    f"Expected {'ON' if state else 'OFF'}"
                )
    
    def set_OVP_state(self, state: bool) -> None:
        # Make sure the user passed in a bool
        if not isinstance(state, bool):
            raise TypeError(f"State must be a bool, got {type(state).__name__}")

        self._resource.write(f"OVP{int(state)}")

        # Check to make sure that the state is what we expect
        hw_OVP_state = Status.OVP_ON in self._status()

        if hw_OVP_state != state:
            raise RuntimeError(
                    f"OCP is {'ON' if hw_OVP_state else 'OFF'}, "
                    f"Expected {'ON' if state else 'OFF'}"
                )

    def get_output_power(self) -> float:
        return float(self._resource.write(f"POWER?"))

    def set_OCP_threshold(self, threshold: float) -> None:
        # Ensure that we are using a float for future arguments
        threshold = self._as_float(threshold, "threshold")

        if threshold < self.MIN_CURRENT or threshold > self.MAX_CURRENT:
            raise ValueError(f"OCP threshold of {threshold} is invalid, must be greater than {self.MIN_CURRENT} and less than {self.MAX_CURRENT}")

        self._resource.write(f"OCP{threshold}")
        # There is no way to check what the OCP threshold is on the KA3005P

    def set_OVP_threshold(self, threshold: float) -> None:
        # Ensure that we are using a float for future arguments
        threshold = self._as_float(threshold, "threshold")

        if threshold < self.MIN_VOLTAGE or threshold > self.MAX_VOLTAGE:
            raise ValueError(f"OVP threshold of {threshold} is invalid, must be between {self.MIN_VOLTAGE} - {self.MAX_VOLTAGE}")
        
        self._resource.write(f"OVP1{threshold}")
        # There is no way to check what the OCP threshold is on the KA3005P
