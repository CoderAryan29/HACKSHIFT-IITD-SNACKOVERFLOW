from __future__ import annotations

from functools import lru_cache
from typing import Any

from agent_service.config import ConfigurationError, configure_langsmith, database_url


@lru_cache(maxsize=1)
def get_checkpointer() -> Any:
    configure_langsmith()
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from psycopg_pool import ConnectionPool
    except ImportError as error:
        raise ConfigurationError(
            "Postgres persistence dependencies are not installed"
        ) from error

    pool = ConnectionPool(
        conninfo=database_url(),
        min_size=1,
        max_size=10,
        open=True,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    )
    pool.wait()
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    return checkpointer


@lru_cache(maxsize=1)
def get_agent():
    configure_langsmith()

    from agent_service.graph.builder import build_agent

    return build_agent(get_checkpointer())
