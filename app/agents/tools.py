from agents import function_tool


@function_tool
def calculate(expression: str) -> str:
    """Evaluate a math expression and return the result. Example: '2 + 3 * 4'"""
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return "Error: expression contains invalid characters"
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@function_tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between celsius, fahrenheit, and kelvin."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value
    if to_unit == "fahrenheit":
        result = celsius * 9 / 5 + 32
    elif to_unit == "kelvin":
        result = celsius + 273.15
    else:
        result = celsius
    return f"{value} {from_unit} = {result:.2f} {to_unit}"


DISTANCE_TO_METERS = {
    "km": 1000, "kilometers": 1000,
    "miles": 1609.344,
    "meters": 1, "m": 1,
    "feet": 0.3048, "ft": 0.3048,
}


@function_tool
def convert_distance(value: float, from_unit: str, to_unit: str) -> str:
    """Convert distance between km, miles, meters, and feet."""
    from_key = from_unit.lower()
    to_key = to_unit.lower()
    if from_key not in DISTANCE_TO_METERS or to_key not in DISTANCE_TO_METERS:
        return f"Error: unsupported unit. Supported: {', '.join(DISTANCE_TO_METERS)}"
    meters = value * DISTANCE_TO_METERS[from_key]
    result = meters / DISTANCE_TO_METERS[to_key]
    return f"{value} {from_unit} = {result:.4f} {to_unit}"


WEIGHT_TO_GRAMS = {
    "kg": 1000, "kilograms": 1000,
    "lbs": 453.592, "pounds": 453.592,
    "grams": 1, "g": 1,
    "ounces": 28.3495, "oz": 28.3495,
}


@function_tool
def convert_weight(value: float, from_unit: str, to_unit: str) -> str:
    """Convert weight between kg, lbs, grams, and ounces."""
    from_key = from_unit.lower()
    to_key = to_unit.lower()
    if from_key not in WEIGHT_TO_GRAMS or to_key not in WEIGHT_TO_GRAMS:
        return f"Error: unsupported unit. Supported: {', '.join(WEIGHT_TO_GRAMS)}"
    grams = value * WEIGHT_TO_GRAMS[from_key]
    result = grams / WEIGHT_TO_GRAMS[to_key]
    return f"{value} {from_unit} = {result:.4f} {to_unit}"
