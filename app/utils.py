from pathlib import Path
import logging
from app.storage import DATA_DIR, load_entry


def get_all_dates_for_class(class_slug: str) -> list[str]:
    """Scans the data directory and returns all entry dates for a class."""
    class_dir = DATA_DIR / class_slug
    if not class_dir.is_dir():
        return []
    try:
        return sorted([d.name for d in class_dir.iterdir() if d.is_dir()])
    except Exception as e:
        logging.exception(f"Error reading dates for class {class_slug}: {e}")
        return []


def get_entry_label(class_slug: str, date_str: str) -> str:
    """Generates a descriptive label for an entry."""
    entry_data = load_entry(class_slug, date_str)
    if not entry_data:
        return f"{date_str} | Entry not found"
    parts = [date_str]
    if entry_data.get("images"):
        num_images = len(entry_data["images"])
        parts.append(f"{num_images} image{('s' if num_images > 1 else '')}")
    if entry_data.get("videos"):
        num_videos = len(entry_data["videos"])
        parts.append(f"{num_videos} video{('s' if num_videos > 1 else '')}")
    if entry_data.get("audio_path"):
        parts.append("audio")
    if entry_data.get("transcript"):
        parts.append("transcript")
    if entry_data.get("typed_text"):
        parts.append("notes")
    if len(parts) > 1:
        return " | ".join(parts)
    else:
        return f"{date_str} | Empty Entry"