import pytest
from app.evals.graders import exact_match, agent_match, contains, get_grader, GraderError, rubric, trajectory


class TestExactMatch:
    def test_match(self):
        assert exact_match({"expected_output": "42"}, {"output": "42"}) == 1.0

    def test_no_match(self):
        assert exact_match({"expected_output": "42"}, {"output": "43"}) == 0.0

    def test_case_insensitive(self):
        assert exact_match({"expected_output": "Hello"}, {"output": "hello"}) == 1.0

    def test_strips_whitespace(self):
        assert exact_match({"expected_output": "42"}, {"output": "  42  "}) == 1.0

    def test_no_expected_output(self):
        assert exact_match({}, {"output": "anything"}) == 1.0


class TestAgentMatch:
    def test_match(self):
        assert agent_match({"expected_agent": "Math_Conversion_Agent"}, {"agent": "Math_Conversion_Agent"}) == 1.0

    def test_no_match(self):
        assert agent_match({"expected_agent": "Math_Conversion_Agent"}, {"agent": "History Agent"}) == 0.0

    def test_no_expected_agent(self):
        assert agent_match({}, {"agent": "anything"}) == 1.0


class TestContains:
    def test_substring_present(self):
        assert contains({"expected_output": "212"}, {"output": "100 celsius = 212.00 fahrenheit"}) == 1.0

    def test_substring_absent(self):
        assert contains({"expected_output": "999"}, {"output": "100 celsius = 212.00 fahrenheit"}) == 0.0

    def test_no_expected_output(self):
        assert contains({}, {"output": "anything"}) == 1.0


class TestGetGrader:
    def test_known_grader(self):
        assert get_grader("exact_match") is exact_match

    def test_unknown_grader(self):
        with pytest.raises(GraderError, match="Unknown grader"):
            get_grader("nonexistent")


class TestRubric:
    @pytest.mark.asyncio
    async def test_rubric_no_rubric_field(self):
        """Should return 1.0 if no rubric defined in case."""
        score = await rubric(case={"input": "hello"}, result={"output": "hi"})
        assert score == 1.0


class TestTrajectory:
    @pytest.mark.asyncio
    async def test_correct_trajectory(self):
        score = await trajectory(
            case={"expected_trajectory": [
                {"type": "agent_handoff", "name_contains": "Math"},
                {"type": "tool_call", "name": "calculate"},
            ]},
            result={"spans": [
                {"type": "agent_handoff", "name": "Triage Agent → Math_Conversion_Agent", "status": "ok"},
                {"type": "tool_call", "name": "calculate", "status": "ok"},
            ]},
        )
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_missing_step(self):
        score = await trajectory(
            case={"expected_trajectory": [
                {"type": "agent_handoff", "name_contains": "Math"},
                {"type": "tool_call", "name": "calculate"},
            ]},
            result={"spans": [
                {"type": "agent_handoff", "name": "Triage Agent → Math_Conversion_Agent", "status": "ok"},
            ]},
        )
        assert score < 1.0

    @pytest.mark.asyncio
    async def test_no_expected_trajectory(self):
        score = await trajectory(case={}, result={"spans": []})
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_wrong_tool(self):
        score = await trajectory(
            case={"expected_trajectory": [{"type": "tool_call", "name": "convert_temperature"}]},
            result={"spans": [{"type": "tool_call", "name": "convert_distance", "status": "ok"}]},
        )
        assert score == 0.0
