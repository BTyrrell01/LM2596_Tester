# Driver for SDS822X oscilloscope
from enum import StrEnum

class Measurement:
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

    def __init__(self, resource, timeout=5000):
        self._resource = resource
        self._resource.timeout = timeout
        self._resource.read_termination = "\n"
        self._resource.write_termination = "\n"

    def idn(self) -> str:
        return self._resource.query("*IDN?")

    def default_state(self) -> None:
        self._resource.write("*RST")

    def set_measurement_type(self, mtype: Measurement, channel: int) -> None:
        # pass mtype through constructor to determine if it is the right type
        try:
            mtype = Measurement(mtype)
        except ValueError:
            valid = ", ".join(m.value for m in Measurement)
            raise ValueError(
                f"{mtype!r} is not a measurement type; must be one of: {valid}"
            ) from None

        self._resource.write(f"MEAS:ADV:P1:TYPE\s{mtype}")
