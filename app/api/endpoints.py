import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner, function_tool

router = APIRouter()
logger = logging.getLogger(__name__)


# --- Tools ---

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

    # Convert to Celsius first
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    # Convert from Celsius to target
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


# --- Specialized Agents ---

math_agent = Agent(
    name="Math_Conversion_Agent",
    handoff_description="Handles math calculations and unit conversions (temperature, distance, weight).",
    instructions=(
        "You are a math and unit conversion specialist. "
        "Use the calculate tool for math expressions. "
        "Use convert_temperature, convert_distance, or convert_weight for unit conversions. "
        "Always use the appropriate tool rather than computing in your head."
    ),
    tools=[calculate, convert_temperature, convert_distance, convert_weight],
)

history_agent = Agent(
    name="History Agent",
    handoff_description="Handles questions about historical events, people, and periods.",
    instructions="You are a history expert. Answer history questions clearly and concisely.",
)

general_agent = Agent(
    name="General Agent",
    handoff_description="Handles general questions that are not about math/conversions or history.",
    instructions="You are a helpful general-purpose assistant. Answer questions clearly and concisely.",
)

# --- Triage Agent ---

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a triage agent. Your job is to route the user's request to the right specialist. "
        "Hand off to the Math & Conversion Agent for calculations and unit conversions. "
        "Hand off to the History Agent for history questions. "
        "Hand off to the General Agent for everything else. "
        "Do not answer questions yourself -- always hand off to a specialist."
    ),
    handoffs=[math_agent, history_agent, general_agent],
)


class ChatRequest(BaseModel):
    messages: list[dict]


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info("Chat request with %d messages", len(request.messages))
    try:
        result = await Runner.run(triage_agent, input=request.messages)
        return ChatResponse(response=result.final_output)
    except Exception as e:
        logger.error("Error processing chat request: %s", e)
        raise HTTPException(status_code=500, detail="Error processing request.")


@router.get("/health")
def health_check():
    return {"status": "Agents Playground API is ready."}
