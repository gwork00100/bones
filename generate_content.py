import numpy as np
from supabase import create_client

# --- CONFIG ---
SUPABASE_URL = "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2VtcnRsbWJ1dnlqa3Jpb3plIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDg4MTc3NCwiZXhwIjoyMDc2NDU3Nzc0fQ.Y5T6WWzp__A0e8Z0p_zaqtNutwrwCOpic6_hkqcCLjY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------
# FUNCTIONS
# ------------------------------
def get_weighted_source():
    weights_resp = supabase.table("prompt_weights").select("*").execute()
    weights = weights_resp.data if weights_resp.data else []

    if not weights:
        return "google"  # fallback

    sources = [w["source"] for w in weights]
    w_values = [w["weight"] for w in weights]
    total = sum(w_values)
    probs = [w_val / total for w_val in w_values] if total > 0 else [1/len(weights)]*len(weights)
    return np.random.choice(sources, p=probs)

def build_prompt():
    src = get_weighted_source()
    return f"Generate trending affiliate content from {src} that maximizes engagement."

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    prompt = build_prompt()
    print("🎯 Generated Prompt:")
    print(prompt)
