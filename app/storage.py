import reflex as rx
from pathlib import Path
import logging
from typing import Optional, Union

DATA_DIR = Path("data/")


def get_entry_dir(class_slug: str, date_str: str) -> Path:
    """Constructs and creates the directory for a given class and date."""
    entry_dir = DATA_DIR / class_slug / date_str
    entry_dir.mkdir(parents=True, exist_ok=True)
    return entry_dir


def save_entry(
    class_slug: str,
    date_str: str,
    images: list[rx.UploadFile],
    videos: list[rx.UploadFile],
    audio_file: Optional[rx.UploadFile],
    typed_text: str,
    transcript: str,
) -> bool:
    """Saves all parts of a classroom artifact entry to the file system."""
    try:
        entry_dir = get_entry_dir(class_slug, date_str)
        if images:
            image_dir = entry_dir / "images"
            image_dir.mkdir(exist_ok=True)
            for image in images:
                with open(image_dir / image.name, "wb") as f:
                    f.write(image.read())
        if videos:
            video_dir = entry_dir / "videos"
            video_dir.mkdir(exist_ok=True)
            for video in videos:
                with open(video_dir / video.name, "wb") as f:
                    f.write(video.read())
        audio_dir = entry_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        audio_path = audio_dir / "recording.wav"
        if audio_file:
            with open(audio_path, "wb") as f:
                f.write(audio_file.read())
        else:
            audio_path.touch()
        (entry_dir / "notes.txt").write_text(typed_text or "")
        (entry_dir / "transcript.txt").write_text(transcript or "")
        logging.info(f"Successfully saved entry for {class_slug} on {date_str}")
        return True
    except Exception as e:
        logging.exception(f"Error saving entry for {class_slug} on {date_str}: {e}")
        return False


def load_entry(
    class_slug: str, date_str: str
) -> Optional[dict[str, Union[list[Path], Path, str]]]:
    """Loads an entry's content from the file system."""
    entry_dir = DATA_DIR / class_slug / date_str
    if not entry_dir.is_dir():
        return None

    def get_files(subdir_name: str) -> list[Path]:
        subdir = entry_dir / subdir_name
        return (
            sorted([p for p in subdir.iterdir() if p.is_file()])
            if subdir.is_dir()
            else []
        )

    try:
        images = get_files("images")
        videos = get_files("videos")
        audio_path = entry_dir / "audio" / "recording.wav"
        if not audio_path.exists() or audio_path.stat().st_size == 0:
            audio_path = None
        notes_path = entry_dir / "notes.txt"
        typed_text = notes_path.read_text() if notes_path.exists() else ""
        transcript_path = entry_dir / "transcript.txt"
        transcript = transcript_path.read_text() if transcript_path.exists() else ""
        return {
            "images": images,
            "videos": videos,
            "audio_path": audio_path,
            "typed_text": typed_text,
            "transcript": transcript,
        }
    except Exception as e:
        logging.exception(f"Error loading entry for {class_slug} on {date_str}: {e}")
        return None