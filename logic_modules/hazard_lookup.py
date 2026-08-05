import json
import os

# 1. Load the data once when the server starts
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, 'map_data.json')
try:
    with open(DATA_PATH, 'r') as f:
        ZIP_DATABASE = json.load(f)
except Exception as e:
    print(f"CRITICAL: Failed to load hazard data: {e}")
    ZIP_DATABASE = {}

def run(val=None, **kwargs):
    """
    Search hazard data by Zip Code.
    Access: /hazard?val=48005
    """
    if not val:
        return "--- REGIONAL HAZARD DATABASE ---\nSystem Online. Please provide a 5-digit ZIP code (?val=XXXXX)."
    
    # 2. Query the dictionary (very fast lookup)
    # Using .strip() in case the user accidentally types a space
    zip_code = str(val).strip()
    info = ZIP_DATABASE.get(zip_code)
    
    if info:
        return (f"--- HAZARD REPORT FOR {zip_code} ---\n"
                f"Location: {info.get('locale', 'Unknown')}\n"
                f"Hazard  : {info.get('hazard', 'N/A')}\n"
                f"Impact  : {info.get('impact', 'N/A')}\n"
                f"Remedy  : {info.get('remedy', 'N/A')}\n\n"
                "Data Source: 2026 Regional Environmental Audit.")
    else:
        return (f"NO DATA FOUND for ZIP {zip_code}.\n"
                "If this is a mistake, contact your district data architect.")