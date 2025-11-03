import random
import time
import datetime
import numpy as np
from datetime import timedelta
from supabase import create_client
from heartbeat_logging import log_heartbeat

# --- CONFIG ---
SUPABASE_URL = "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2VtcnRsbWJ1dnlqa3Jpb3plIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDg4MTc3NCwiZXhwIjoyMDc2NDU3Nzc0fQ.Y5T6WWzp__A0e8Z0p_zaqtNutwrwCOpic6_hkqcCLjY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VALID_SOURCES = ["Twitter", "Google", "Reddit", "Medium", "LinkedIn"]
MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds

# ------------------------------
# FUNCTIONS
# ------------------------------

def seed_fake_performance():
    print("⚠️ content_performance is empty. Seeding fake data...")
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
    print("✅ Fake data seeded.")

def fix_missing_sources(performance):
    for row in performance:
        if not row.get("source"):
            new_source = random.choice(VALID_SOURCES)
            row["source"] = new_source
            supabase.table("content_performance").update({"source": new_source}).eq("asin", row["asin"]).execute()
    return performance

def analyze_performance():
    trends = supabase.table("trends").select("*").execute().data
    performance = supabase.table("content_performance").select("*").execute().data

    if not performance:
        seed_fake_performance()
        performance = supabase.table("content_performance").select("*").execute().data

    if not trends:
        print("⚠️ trends table is empty. Exiting.")
        log_heartbeat("failure", "Trends table empty. Analysis skipped.")
        return

    performance = fix_missing_sources(performance)

    # Compute CTR
    for row in performance:
        clicks = row.get("clicks", 0)
        conversions = row.get("conversions", 0)
        row["ctr"] = conversions / clicks if clicks else 0

    # Organize by source
    performance_by_source = {}
    for row in performance:
        src = row["source"]
        performance_by_source.setdefault(src, []).append(row["ctr"])

    # Calculate weights
    avg_scores = {src: np.mean(scores) for src, scores in performance_by_source.items()}
    max_score = max(avg_scores.values(), default=1)
    new_weights = {src: (score / max_score) + 0.5 for src, score in avg_scores.items()}

    # Update prompt_weights
    for src, w in new_weights.items():
        supabase.table("prompt_weights").upsert({
            "source": src,
            "weight": round(w, 2),
            "performance_score": round(avg_scores[src], 4),
            "last_analyzed": datetime.datetime.utcnow().isoformat()
        }).execute()

    log_heartbeat("success", f"Updated weights: {new_weights}")
    print("🔥 Updated weights:", new_weights)

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            analyze_performance()
            break
        except Exception as e:
            attempt += 1
            log_heartbeat("failure", f"Attempt {attempt} failed: {str(e)}")
            print(f"[Performance Analyzer] Attempt {attempt} failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            if attempt >= MAX_RETRIES:
                print("[Performance Analyzer] Max retries reached. Exiting.")
