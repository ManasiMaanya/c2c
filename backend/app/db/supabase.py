import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is not configured")

if not SUPABASE_PUBLISHABLE_KEY:
    raise ValueError("SUPABASE_PUBLISHABLE_KEY is not configured")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY,
)