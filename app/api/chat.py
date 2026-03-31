import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
)
from agents.memory import SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent

from app.config import settings
from app.database import create_run, complete_run
from app.agents.definitions import triage_agent
from app.schemas import ChatRequest
from app.tracing.collector import TraceCollector

router = APIRouter()
logger = logging.getLogger(__name__)


def sse_event(event_type: str, **kwargs) -> str:
    return json.dumps({"type": event_type, **kwargs}) + "\n\n"


async def stream_agent_response(message: str, session_id: str):
    run_id = create_run(settings.db_path, session_id=session_id, input_text=message)
    collector = TraceCollector(run_id=run_id)
    yield sse_event("run_started", run_id=run_id)

    session = SQLiteSession(session_id=session_id, db_path=settings.db_path)
    output_chunks: list[str] = []
    final_agent_name: str | None = None
    previous_agent_name: str = "Triage Agent"
    # Maps call_id -> (tool_name, arguments) for correlating tool calls with their outputs
    pending_tool_calls: dict[str, tuple[str, str | None]] = {}

    try:
        result = Runner.run_streamed(triage_agent, input=message, session=session)
        async for event in result.stream_events():
            if event.type == "agent_updated_stream_event":
                new_name = event.new_agent.name
                collector.record_handoff(previous_agent_name, new_name)
                previous_agent_name = new_name
                final_agent_name = new_name
                yield sse_event("status", message=f"Routed to {new_name}")
            elif event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                output_chunks.append(event.data.delta)
                yield sse_event("token", content=event.data.delta)
            elif event.type == "run_item_stream_event":
                if event.name == "tool_called" and isinstance(event.item, ToolCallItem):
                    raw = event.item.raw_item
                    tool_name = getattr(raw, "name", None) or (raw.get("name") if isinstance(raw, dict) else None)
                    call_id = getattr(raw, "call_id", None) or (raw.get("call_id") if isinstance(raw, dict) else None)
                    arguments = getattr(raw, "arguments", None) or (raw.get("arguments") if isinstance(raw, dict) else None)
                    if tool_name and call_id:
                        pending_tool_calls[call_id] = (tool_name, arguments)
                elif event.name == "tool_output" and isinstance(event.item, ToolCallOutputItem):
                    raw = event.item.raw_item
                    call_id = (raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None))
                    output = event.item.output
                    output_str = output if isinstance(output, str) else json.dumps(output) if output is not None else None
                    if call_id and call_id in pending_tool_calls:
                        tool_name, arguments = pending_tool_calls.pop(call_id)
                        collector.record_tool_call(tool_name, input_data=arguments, output_data=output_str)
                    elif call_id:
                        # Output without a matched call — record with unknown name
                        collector.record_tool_call("unknown", output_data=output_str)

        full_output = "".join(output_chunks)
        complete_run(
            settings.db_path, run_id,
            output=full_output, status="completed",
            final_agent=final_agent_name,
        )
        collector.flush(settings.db_path)

    except InputGuardrailTripwireTriggered as e:
        logger.warning("Input guardrail triggered: %s", e)
        collector.record_error("input_guardrail", str(e))
        collector.flush(settings.db_path)
        complete_run(settings.db_path, run_id, output="", status="guardrail_blocked", final_agent="guardrail")
        yield sse_event("error", message="Sorry, I can't process that request. Please rephrase your message.")

    except OutputGuardrailTripwireTriggered as e:
        logger.warning("Output guardrail triggered: %s", e)
        collector.record_error("output_guardrail", str(e))
        collector.flush(settings.db_path)
        complete_run(settings.db_path, run_id, output="", status="guardrail_blocked", final_agent="guardrail")
        yield sse_event("error", message="Sorry, the response was blocked because it may contain sensitive data.")

    except Exception as e:
        logger.error("Error processing chat request: %s", e)
        collector.record_error("runtime", str(e))
        collector.flush(settings.db_path)
        complete_run(settings.db_path, run_id, output="", status="failed")
        yield sse_event("error", message="An error occurred while processing your request.")


@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info("Chat request - session: %s", request.session_id)
    return StreamingResponse(
        stream_agent_response(request.message, request.session_id),
        media_type="text/event-stream",
    )


@router.get("/health")
def health_check():
    return {"status": "OpenAI Agents Lab API is ready."}
