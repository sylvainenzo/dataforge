import time
from http.cookies import SimpleCookie

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.audit import log_execution
from app.auth import InvalidTokenError, verify_access_token
from app.config import settings
from app.orchestrator import LocalSubprocessOrchestrator
from app.rate_limit import check_execution_rate_limit

app = FastAPI(title="DataForge Execution Gateway", version="0.1.0")

# See app/orchestrator.py's module docstring before touching this line.
orchestrator = LocalSubprocessOrchestrator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


class RunRequest(BaseModel):
    code: str
    language: str = "python"


def _extract_access_token(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    jar = SimpleCookie()
    jar.load(cookie_header)
    morsel = jar.get("access_token")
    return morsel.value if morsel else None


@app.websocket("/ws/execution")
async def execution_socket(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin not in settings.cors_origins:
        await websocket.close(code=4403)
        return

    token = _extract_access_token(websocket.headers.get("cookie"))
    if token is None:
        await websocket.close(code=4401)
        return

    try:
        user_id = verify_access_token(token)
    except InvalidTokenError:
        await websocket.close(code=4401)
        return

    if not await check_execution_rate_limit(str(user_id)):
        await websocket.close(code=4429)
        return

    await websocket.accept()

    try:
        while True:
            payload = await websocket.receive_json()
            run = RunRequest.model_validate(payload)

            started = time.monotonic()
            exit_code = "unknown"
            async for chunk in orchestrator.run(code=run.code, language=run.language):
                if chunk.stream == "exit":
                    exit_code = chunk.data
                await websocket.send_json({"stream": chunk.stream, "data": chunk.data})

            duration_ms = int((time.monotonic() - started) * 1000)
            await log_execution(user_id=user_id, language=run.language, exit_code=exit_code, duration_ms=duration_ms)
    except WebSocketDisconnect:
        pass
