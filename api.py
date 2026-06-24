import logging
import time

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agent_service import run_agent
from agent_errors import AgentServiceUnavailableError

logger = logging.getLogger(
    "personal_knowledge_agent.api"
)


app = FastAPI(
    title="Personal Knowledge Agent API",
    version ="0.1.0"
)


class ChatRequest(BaseModel):
    question:str = Field(
        min_length=1,
        max_length=500
    )


class ChatResponse(BaseModel):
    answer:str
    sources:list[int] = Field(default_factory=list)
    step_count:int = Field(ge=0)


def get_chat_outcome(status_code:int)->str:
    if status_code == 200:
        return "success"
    
    if status_code == 422:
        return "request_validation_failed"
    
    if status_code == 503:
        return "agent_service_unavailable"
    
    if status_code == 500:
        return "internal_server_error"
    
    return "unexpected_status"



@app.middleware("http")
async def log_chat_request(request: Request, call_next):
    if request.url.path != "/chat":
        return await call_next(request)

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        logger.error(
            "event=chat_request_completed "
            "method=%s path=%s status_code=500 "
            "outcome=internal_server_error duration_ms=%s",
            request.method,
            request.url.path,
            duration_ms
        )

        raise

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    logger.info(
        "event=chat_request_completed "
        "method=%s path=%s status_code=%s "
        "outcome=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        get_chat_outcome(response.status_code),
        duration_ms
    )

    return response




@app.get("/health")
def health():
    return {
        "status":"ok"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = run_agent(request.question)

    except AgentServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "agent_service_unavailable",
                "message": "Agent 服务暂时不可用，请稍后再试。"
            }
        )

    return ChatResponse(
        answer=response["answer"],
        sources=response["sources"],
        step_count=response["step_count"]
    )