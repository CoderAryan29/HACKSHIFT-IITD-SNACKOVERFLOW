from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(RuntimeError):
    pass


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is not configured")
    return value


def google_api_key() -> str:
    return required_env("GOOGLE_API_KEY")


def database_url() -> str:
    return required_env("DATABASE_URL")


def gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def langsmith_tracing_enabled() -> bool:
    return os.getenv("LANGCHAIN_TRACING_V2", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def langsmith_api_key() -> str:
    return required_env("LANGCHAIN_API_KEY")


def langsmith_project() -> str:
    return os.getenv("LANGCHAIN_PROJECT", "kisansetu-agent").strip() or "kisansetu-agent"


def configure_langsmith() -> bool:
    if not langsmith_tracing_enabled():
        return False

    api_key = langsmith_api_key()
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key
    os.environ["LANGCHAIN_PROJECT"] = langsmith_project()
    return True