# This file name is Storage.py
"""Persistence layer for the Country Relocation & Culture Guide app.

Previously this only appended plain text to a single .txt file, which made it
impossible to list or preview individual saves. It now keeps structured JSON
records (one per saved profile / guide / comparison) so the Streamlit UI can
show a browsable "Saved Travel Profiles & Guides" library with previews.
"""
import os
import json
import uuid
from datetime import datetime

# Cross-platform save location.
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Country_Guide_Saves")
DATA_FILE = os.path.join(SAVE_DIR, "saved_data.json")

PROFILE = "profile"
GUIDE = "guide"
COMPARISON = "comparison"


def _load():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _save_all(records):
    os.makedirs(SAVE_DIR, exist_ok=True)
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, DATA_FILE)


def _add_record(record_type, title, content, meta=None):
    records = _load()
    record = {
        "id": uuid.uuid4().hex,
        "type": record_type,
        "title": title or "Untitled",
        "content": content,
        "meta": meta or {},
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    records.append(record)
    try:
        _save_all(records)
        return True, f"Saved '{record['title']}' to your library."
    except OSError as e:
        return False, f"Could not save: {e}"


def save_country_profile(info_dict):
    """Pass the dict returned by rest_country_api.get_country_info()."""
    if not info_dict:
        return False, "Nothing to save."
    title = info_dict.get("Name", "Unknown Country")
    meta = {"flag": info_dict.get("Flag Image URL")}
    return _add_record(PROFILE, title, info_dict, meta)


def save_travel_guide(guide_text, country_name=None):
    """Pass the string returned by google_api.generate_travel_guide()."""
    if not guide_text:
        return False, "Nothing to save."
    title = country_name or "Travel Guide"
    return _add_record(GUIDE, title, guide_text)


def save_comparison(comparison_text, country_a=None, country_b=None):
    """Pass the string returned by google_api.generate_comparison()."""
    if not comparison_text:
        return False, "Nothing to save."
    if country_a and country_b:
        title = f"{country_a} vs {country_b}"
    else:
        title = "Country Comparison"
    meta = {"country_a": country_a, "country_b": country_b}
    return _add_record(COMPARISON, title, comparison_text, meta)


def get_all_records():
    """Newest first."""
    return list(reversed(_load()))


def get_record(record_id):
    for r in _load():
        if r["id"] == record_id:
            return r
    return None


def delete_record(record_id):
    records = _load()
    filtered = [r for r in records if r["id"] != record_id]
    if len(filtered) == len(records):
        return False, "Record not found."
    try:
        _save_all(filtered)
        return True, "Deleted."
    except OSError as e:
        return False, f"Could not delete: {e}"
