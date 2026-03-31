import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    Runner,
)
from agents.memory import SQLiteSession
from openai.types.responses import ResponseTextDeltaEvent

from app.config import settings
from app.database import create_run, complete_run
from app.agents.definitions import triage_agent
from app.schemas import ChatRequest

router = APIRouter()
logger = logging.getLogger(__name__)


def sse_event(event_type: str, **kwargs) -> str:
    return json.dumps({"type": event_type, **kwargs}) + "\n\n"


async def stream_agent_response(message: str, session_id: str):
    run_id = create_run(settings.db_path, session_id=session_id, input_text=message)
    yield sse_event("run_started", run_id=run_id)

    session = SQLiteSession(session_id=session_id, db_path=settings.db_path)
    output_chunks: list[str] = []
    final_agent_name: str | None = None

    try:
        result = Runner.run_streamed(triage_agent, input=message, session=session)
        async for event in result.stream_events():
            if event.type == "agent_updated_stream_event":
                final_agent_name = event.new_agent.name
                yield sse_event("status", message=f"Routed to {event.new_agent.name}")
            elif event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                output_chunks.append(event.data.delta)
                yield sse_event("token", content=event.data.delta)

        full_output = "".join(output_chunks)
        complete_run(
            settings.db_path, run_id,
            output=full_output, status="completed",
            final_agent=final_agent_name,
        )

    except InputGuardrailTripwireTriggered as e:
        logger.warning("Input guardrail triggered: %s", e)
        complete_run(settings.db_path, run_id, output="", status="guardrail_blocked", final_agent="guardrail")
        yield sse_event("error", message="Sorry, I can't process that request. Please rephrase your message.")

    except OutputGuardrailTripwireTriggered as e:
        logger.warning("Output guardrail triggered: %s", e)
        complete_run(settings.db_path, run_id, output="", status="guardrail_blocked", final_agent="guardrail")
        yield sse_event("error", message="Sorry, the response was blocked because it may contain sensitive data.")

    except Exception as e:
        logger.error("Error processing chat request: %s", e)
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
