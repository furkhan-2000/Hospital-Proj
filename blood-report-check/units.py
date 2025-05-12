from pint import UnitRegistry
from pint.errors import UndefinedUnitError

ureg = UnitRegistry()
Q_ = ureg.Quantity

# Define unit aliases mapping to standard units
UNIT_ALIASES = {
    "mg/dl": "milligram / deciliter",
    "mmol/l": "millimole / liter",
    "g/l": "gram / liter",
    "mg/l": "milligram / liter",
    "μmol/l": "micromole / liter",
    "iu/l": "international_unit / liter",
    "cells/hpf": "count / high_power_field",
    "cfu/ml": "colony_forming_unit / milliliter",
    "sp hpf": "count / high_power_field",
}

def normalize_unit(unit: str) -> str:
    """
    Normalize common unit variants to Pint-compatible format.
    Returns a cleaned version or raises an error if invalid.
    """
    if not unit:
        return ""
    key = unit.strip().lower()
    return UNIT_ALIASES.get(key, key)  # fallback to user input if no alias

def convert_value(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a value from one unit to another using Pint.
    Raises ValueError if conversion is not possible.
    """
    try:
        from_unit_norm = normalize_unit(from_unit)
        to_unit_norm = normalize_unit(to_unit)
        quantity = Q_(value, from_unit_norm)
        return quantity.to(to_unit_norm).magnitude
    except UndefinedUnitError as e:
        raise ValueError(f"Unrecognized unit: {e}")
    except Exception as e:
        raise ValueError(f"Conversion failed: {e}")
