from fastapi import APIRouter, FastAPI

from agent_service.api.chat import router as chat_router

router = APIRouter(prefix="/agent/v1")
router.include_router(chat_router)


def create_app() -> FastAPI:
    app = FastAPI(title="KisanSetu Agent Service")
    app.get("/health")(health)
    app.include_router(router)
    return app


def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent_service"}


app = create_app()