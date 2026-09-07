import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("supabase")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")


class MockTable:
    def __init__(self, name: str):
        self.name = name
        self._data = [
            {"id": "ag_8801_cs", "name": "Customer Support Agent", "model": "gemini-2.5-flash", "budget": 100.00, "status": "active"},
            {"id": "ag_8802_code", "name": "Code Assistant Agent", "model": "gemini-3.1-pro", "budget": 150.00, "status": "active"},
            {"id": "ag_8803_fin", "name": "Finance Analytics Bot", "model": "gemini-2.5-flash-lite", "budget": 50.00, "status": "paused"}
        ]

    def select(self, *args, **kwargs):
        return self

    def insert(self, data, *args, **kwargs):
        if isinstance(data, list):
            self._data.extend(data)
        elif isinstance(data, dict):
            self._data.append(data)
        return self

    def update(self, *args, **kwargs):
        return self

    def delete(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, count: int, *args, **kwargs):
        return self

    def execute(self):
        class Response:
            def __init__(self, data):
                self.data = data
                self.count = len(data) if isinstance(data, list) else 1

        return Response(self._data)


class MockClient:
    def table(self, name: str):
        return MockTable(name)


supabase = None

if SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY:
    try:
        from supabase import Client, create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
    except Exception as exc:
        logger.warning("Failed to initialize Supabase client (%s). Using in-memory fallback.", exc)
        supabase = MockClient()
else:
    supabase = MockClient()