# hardware/drivers/validation.py
# Argument validation shared by psu and scope drivers

def as_float(value, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        return float(value)

def as_float_in_range(value, name: str, low: float, high: float, unit: str = "") -> float:
      value = as_float(value, name)
      if not low <= value <= high:
          u = f" {unit}" if unit else ""
          raise ValueError(f"{name} of {value}{u} is outside the allowed range {low} - {high}{u}")
      return value

def as_int(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    return int(value)

def as_int_in(value, name: str, allowed) -> int:
    value = as_int(value, name)
    if value not in allowed:
        raise ValueError(f"{name} of {value} is invalid, must be one of {list(allowed)}")
    return value
