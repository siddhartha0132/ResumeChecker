import json
import os

STORAGE_FILE = os.path.join(os.path.dirname(__file__), 'candidates_data.json')


def save_candidates(candidates_db: dict):
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(candidates_db, f, indent=2)
    except Exception as e:
        print(f"Storage save error: {e}")


def load_candidates() -> dict:
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Storage load error: {e}")
    return {}
