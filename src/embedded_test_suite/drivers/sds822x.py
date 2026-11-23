# Driver for SDS822X oscilloscope
from enum import StrEnum
from .validation import as_int_in

class Measurement(StrEnum):
    PKPK = "PKPK"
    MAX = "MAX"
    MIN = "MIN"
    AMPL = "AMPL"
    TOP = "TOP"
    BASE = "BASE"
    LEVELX = "LEVELX"
    CMEAN = "CMEAN"
    MEAN = "MEAN"
    STDEV = "STDEV"
    VSTD = "VSTD"
    RMS = "RMS"
    CRMS = "CRMS"
    MEDIAN = "MEDIAN"
    CMEDIAN = "CMEDIAN"
    OVSN = "OVSN"
    FPRE = "FPRE"
    OVSP = "OVSP"
    RPRE = "RPRE"
    ULOWer = "ULOWer"
    PER = "PER"
    FREQ = "FREQ"
    TMAX = "TMAX"
    TMIN = "TMIN"
    PWID = "PWID"
    NWID = "NWID"
    DUTY = "DUTY"
    NDUTY = "NDUTY"
    WID = "WID"
    NBWID = "NBWID"
    DELAY = "DELAY"
    TIMEL = "TIMEL"
    RISE = "RISE"
    FALL = "FALL"
    RISE10T90 = "RISE10T90"
    FALL90T10 = "FALL90T10"
    CCJ = "CCJ"
    PAREA = "PAREA"
    NAREA = "NAREA"
    AREA = "AREA"
    ABSAREA = "ABSAREA"
    CYCLES = "CYCLES"
    EDGES = "EDGES"
    REDGES = "REDGES"
    FEDGES = "FEDGES"
    PPULSES = "PPULSES"
    NPULSES = "NPULSES"
    PHA = "PHA"
    SKEW = "SKEW"
    FRR = "FRR"
    FRF = "FRF"
    FFR = "FFR"
    FFF = "FFF"
    LRR = "LRR"
    LRF = "LRF"
    LFR = "LFR"
    LFF = "LFF"
    PACArea = "PACArea"
    NACArea = "NACArea"
    ACArea = "ACArea"
    ABSACArea = "ABSACArea"
    PSLOPE = "PSLOPE"
    NSLOPE = "NSLOPE"
    TSR = "TSR"
    TSF = "TSF"
    THR = "THR"
    THF = "THF"
    DITMe1 = "DITMe1-4"

class Sds822x:
    CHANNELS = [1, 2]       # This oscilloscope has 2 channels

    def __init__(self, resource, timeout=15000):
        self._resource = resource
        self._resource.timeout = timeout
        self._resource.read_termination = "\n"
        self._resource.write_termination = "\n"

    def _check_errors(self) -> None:
        """Raise if the scope logged an error for the last command."""
        reply = self._resource.query("SYST:ERR?").strip()
        if not reply.startswith("0,"):
            raise RuntimeError(f"scope reported: {reply}")

    def _to_float(self, reply: str, context: str) -> float:
        text = reply.strip()
        if text.startswith("*"):
            raise RuntimeError(f"{context} is not measurable on the current signal")
        try:
            return float(text)
        except ValueError:
            raise RuntimeError(f"unparseable reply for {context}: {reply!r}") from None

    def idn(self) -> str:
        return self._resource.query("*IDN?")

    def default_state(self) -> None:
        self._resource.write("*RST")
        self._check_errors()

    def auto_set(self):
        self._resource.write("*CLS")
        self._resource.write(":AUToset")
        self._resource.query("*OPC?")
        self._check_errors()

    def _set_measurement_channel(self, channel) -> None:
        channel = as_int_in(channel, "channel", self.CHANNELS)
        self._resource.write(f":MEASure:SIMPle:SOURce C{channel}")
        self._check_errors()

    def get_measurement_channel(self) -> int:
        return self._resource.query(f":MEASure:SIMPle:SOURce?")

    def get_measurement_value(self, mtype: Measurement, channel: int) -> str:
        # pass mtype through constructor to determine if it is the right type
        try:
            mtype = Measurement(mtype)
        except ValueError:
            valid = ", ".join(m.value for m in Measurement)
            raise ValueError(
                f"{mtype!r} is not a measurement type; must be one of: {valid}"
            ) from None
        
        channel = as_int_in(channel, "channel", self.CHANNELS)
        self._set_measurement_channel(channel)

        value = self._resource.query(f"MEAS:SIMP:VAL? {Measurement(mtype)}")
        return self._to_float(value, f"{mtype} on C{channel}")
