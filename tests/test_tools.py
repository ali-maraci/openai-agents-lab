import asyncio
import json

import pytest

from agents.tool_context import ToolContext
from agents.usage import Usage


def invoke(tool, **kwargs):
    """Helper to synchronously invoke a FunctionTool with keyword arguments."""
    async def _run():
        ctx = ToolContext(None, Usage(), tool.name, "call_test", json.dumps(kwargs))
        return await tool.on_invoke_tool(ctx, json.dumps(kwargs))

    return asyncio.run(_run())


class TestCalculate:
    def setup_method(self):
        from app.agents.tools import calculate
        self.tool = calculate

    def test_simple_addition(self):
        result = invoke(self.tool, expression="2 + 3")
        assert "5" in result

    def test_invalid_expression_returns_error(self):
        result = invoke(self.tool, expression="import os")
        assert "Error" in result or "invalid" in result.lower()


class TestConvertTemperature:
    def setup_method(self):
        from app.agents.tools import convert_temperature
        self.tool = convert_temperature

    def test_celsius_to_fahrenheit(self):
        result = invoke(self.tool, value=100.0, from_unit="celsius", to_unit="fahrenheit")
        assert "212" in result

    def test_fahrenheit_to_celsius(self):
        result = invoke(self.tool, value=32.0, from_unit="fahrenheit", to_unit="celsius")
        assert "0" in result


class TestConvertDistance:
    def setup_method(self):
        from app.agents.tools import convert_distance
        self.tool = convert_distance

    def test_km_to_miles(self):
        result = invoke(self.tool, value=1.0, from_unit="km", to_unit="miles")
        assert "0.6214" in result

    def test_unsupported_unit_returns_error(self):
        result = invoke(self.tool, value=1.0, from_unit="parsec", to_unit="km")
        assert "Error" in result


class TestConvertWeight:
    def setup_method(self):
        from app.agents.tools import convert_weight
        self.tool = convert_weight

    def test_kg_to_lbs(self):
        result = invoke(self.tool, value=1.0, from_unit="kg", to_unit="lbs")
        assert "2.2046" in result

    def test_unsupported_unit_returns_error(self):
        result = invoke(self.tool, value=1.0, from_unit="stone", to_unit="kg")
        assert "Error" in result
