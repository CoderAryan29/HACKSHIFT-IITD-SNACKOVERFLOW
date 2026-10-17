from sqlalchemy import text
from core_api.db.session import get_engine

try:
    with get_engine().connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("SUCCESS: Supabase database connected!")
        print("Test result:", result.scalar())
except Exception as error:
    print("Database connection failed.")
    print(type(error).__name__ + ":", str(error))