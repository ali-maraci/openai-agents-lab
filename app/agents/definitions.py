from agents import Agent

from app.agents.tools import (
    calculate,
    convert_temperature,
    convert_distance,
    convert_weight,
)
from app.agents.guardrails import (
    prompt_injection_guardrail,
    inappropriate_content_guardrail,
    sensitive_data_guardrail,
)


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
    input_guardrails=[prompt_injection_guardrail, inappropriate_content_guardrail],
    output_guardrails=[sensitive_data_guardrail],
)
