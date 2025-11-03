from supabase import create_client
import os, random, datetime
from datetime import timedelta

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_SOURCES = ["Twitter", "Google", "Reddit", "Medium", "LinkedIn"]

def seed_content_performance():
    """Seed fake data into content_performance table if empty."""
    # Check if table is empty
    result = supabase.table("content_performance").select("id", count="exact").execute()
    count = result.count if hasattr(result, "count") else len(result.data)

    if count == 0:
        print("⚠️ content_performance table is empty. Seeding automatically...")
        fake_rows = []
        for i in range(1, 6):
            asin = f"FAKE{i:03d}"
            source = random.choice(VALID_SOURCES)
            clicks = random.randint(20, 150)
            conversions = random.randint(0, clicks // 5)
            revenue = round(conversions * random.uniform(5, 50), 2)
            recorded_at = datetime.datetime.utcnow() - timedelta(days=random.randint(0, 5))
            fake_rows.append({
                "asin": asin,
                "source": source,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": revenue,
                "recorded_at": recorded_at.isoformat()
            })
        supabase.table("content_performance").insert(fake_rows).execute()
        print("✅ content_performance seeded automatically.")
    else:
        print(f"✅ content_performance table already has {count} rows. No seeding needed.")

if __name__ == "__main__":
    seed_content_performance()
