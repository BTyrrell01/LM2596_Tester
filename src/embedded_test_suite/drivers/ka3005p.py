# driver for Korad KA3005P power supply

class Ka3005p:
    def __init__(self, resource):
        self._resource = resource
        self.timeout = 5000     # Timeout in ms

