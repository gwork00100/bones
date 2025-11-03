from supabase import create_client

SUPABASE_URL = "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = "sb_secret_84QbW2noWzcABMsv6XWJWw_vv6ZTKbF"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

data = {
    "title": "Test Insert",
    "link": "https://example.com",
    "keyword": "test",
    "interest": None,
    "fetched_at": "2025-01-01T00:00:00Z"
}

res = supabase.table("trends").insert(data).execute()

print(res)
