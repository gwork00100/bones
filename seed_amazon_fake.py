import random
from datetime import datetime, timedelta
from supabase import create_client
import os

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "sb_secret_84QbW2noWzcABMsv6XWJWw_vv6ZTKbF"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- AUTO-SEED Amazon trends ---
print("⚡ Seeding fake Amazon trends...")
fake_products = [
    {"id": f"FAKE_AMZ_{i:03d}", "title": f"Amazon Product Test {i}", "source": "amazon"}
    for i in range(1, 6)
]

supabase.table("trends").upsert(fake_products).execute()
print("✅ Fake trends inserted.")

# --- AUTO-SEED content_performance ---
print("⚡ Seeding fake Amazon performance data...")
fake_perf = []
for prod in fake_products:
    clicks = random.randint(20, 150)
    conversions = random.randint(0, clicks // 5)
    revenue = round(conversions * random.uniform(5, 50), 2)
    recorded_at = datetime.utcnow() - timedelta(days=random.randint(0, 5))
    fake_perf.append({
        "content_id": prod["id"],
        "source": prod["source"],
        "clicks": clicks,
        "conversions": conversions,
        "revenue": revenue,
        "recorded_at": recorded_at.isoformat()
    })

supabase.table("content_performance").upsert(fake_perf).execute()
print("✅ Fake content_performance inserted.")

# --- OPTIONAL: Print table preview ---
trends = supabase.table("trends").select("*").execute().data
performance = supabase.table("content_performance").select("*").execute().data

print("\n🔥 Current trends:")
for t in trends:
    print(t)

print("\n🔥 Current content_performance:")
for p in performance:
    print(p)
