
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from workspace-app/.env
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_database_url() -> str:
    """Return the configured database URL or raise a clear error."""
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure it in workspace-app/.env."
        )

    # SQLAlchemy should use the installed psycopg v3 driver.
    if DATABASE_URL.startswith("postgresql://"):
        return DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return DATABASE_URL
