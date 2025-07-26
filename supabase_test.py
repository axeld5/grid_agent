import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")          # e.g. https://abcd1234.supabase.co
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")     # or SERVICE_ROLE key if server-side

def supabase_get(table, select="*"):
    """
    filters: list of (key, value) pairs like
             (list so you can repeat the same column with different operators)
    order:   tuple like ("created_at", "desc") or ("name","asc.nullslast")
    range_:  (start, end) to paginate with the Range header (inclusive)
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = [("select", select)]

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Accept": "application/json",
        "Prefer": "count=exact"  # returns Content-Range header with total
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    total = resp.headers.get("Content-Range")  # e.g. "0-9/123"
    return resp.json(), total

# --- Examples for your 3 tables (replace names/columns as needed) ---

# 1) users: latest 10 users
grid_data, grid_data_count = supabase_get(
    "grid_data",
)

# 2) orders: all paid orders, first page (0–99)
temperature_data, temperature_data_count = supabase_get(
    "temperature_data",
)

# 3) products: price between 10 and 100, name contains 'tee', ordered by price asc
network_data, network_data_count = supabase_get(
    "network_data",
)

print(grid_data_count, grid_data[:1])
print(temperature_data_count, temperature_data[:2])
print(network_data_count, network_data[:2])