from fastapi import APIRouter, FastAPI

from agent_service.api.chat import router as chat_router

router = APIRouter(prefix="/agent/v1")
router.include_router(chat_router)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent_service"}


def create_app() -> FastAPI:
    app = FastAPI(title="KisanSetu Agent Service")
    app.include_router(router)
    return app





app = create_app()