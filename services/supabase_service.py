from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

db_supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)