import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner

router = APIRouter()
logger = logging.getLogger(__name__)

agent = Agent(
    name="Assistant",
    instructions="You answer history questions clearly and concisely",
)


class ChatRequest(BaseModel):
    messages: list[dict]


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info("Chat request with %d messages", len(request.messages))
    try:
        result = await Runner.run(agent, input=request.messages)
        return ChatResponse(response=result.final_output)
    except Exception as e:
        logger.error("Error processing chat request: %s", e)
        raise HTTPException(status_code=500, detail="Error processing request.")


@router.get("/health")
def health_check():
    return {"status": "Agents Playground API is ready."}
