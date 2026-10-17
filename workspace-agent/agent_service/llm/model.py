from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from agent_service.config import gemini_model, google_api_key


def get_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=gemini_model(),
        google_api_key=google_api_key(),
        temperature=0,
        timeout=30,
        max_retries=2,
    )
