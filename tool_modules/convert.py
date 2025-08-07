def energy_convert(value, unit, elec=False):
    """
    Converts energy or emission values to more readable units.

    Parameters:
        value (float): The input value.
        unit (str): Input unit. Can be 'GJ', 't', or 'kt'.
        elec (bool): If True, energy is converted to MWh/TWh.

    Returns:
        (converted_value, new_unit): Tuple with converted float and unit.
    """
    # Handle emissions (convert to tonnes first)
    if unit == "kt":
        if value >= 1_000:
            return round(value / 1_000_000, 2), "Mt"
        else:
            return round(value, 2), "kt"

    if unit == "t":
        if value >= 1_000_000:
            return round(value / 1_000_000, 2), "Mt"
        elif value >= 1_000:
            return round(value / 1_000, 2), "kt"
        else:
            return round(value, 2), "t"

    # Handle electricity
    if elec:
        # 1 GJ = 0.277778 MWh
        value_mwh = value * 0.277778
        if value_mwh >= 1_000_000:
            return round(value_mwh / 1_000_000), "TWh"
        else:
            return round(value_mwh), "MWh"

    # Handle generic energy conversion from GJ
    if unit == "GJ":
        if value >= 1_000_000:
            return round(value / 1_000_000), "PJ"
        elif value >= 1_000:
            return round(value / 1_000), "TJ"
        else:
            return round(value), "GJ"

    # Fallback if unknown unit
    return round(value), unit
