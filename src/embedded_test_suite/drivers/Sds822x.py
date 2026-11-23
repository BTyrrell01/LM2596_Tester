# Driver for SDS822X oscilloscope

class Sds822x:

    def __init__(self, resource, timeout=5000):
        self._resource = resource
        self._resource.timeout = timeout
        self._resource.read_termination = "\n"
        self._resource.write_termination = "\n"

    def idn(self) -> str:
        return self._resource.query("*IDN?")

    def default_state(self) -> None:
        self._resource.write("*RST")
