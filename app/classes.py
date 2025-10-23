import reflex as rx
from typing import TypedDict


class ClassInfo(TypedDict):
    name: str
    slug: str
    emoji: str
    accent_color: str


CLASS_INFO: dict[str, ClassInfo] = {
    "ap-chemistry": {
        "name": "AP Chemistry",
        "slug": "ap-chemistry",
        "emoji": "🧪",
        "accent_color": "#3B82F6",
    },
    "chemistry": {
        "name": "Chemistry",
        "slug": "chemistry",
        "emoji": "⚗️",
        "accent_color": "#10B981",
    },
    "pltw-medical-interventions": {
        "name": "PLTW Medical Interventions",
        "slug": "pltw-medical-interventions",
        "emoji": "🏥",
        "accent_color": "#F59E0B",
    },
}
SUPPORTED_IMAGES = [".png", ".jpg", ".jpeg", ".webp", ".heic"]
SUPPORTED_VIDEOS = [".mp4", ".mov", ".avi", ".mkv"]
SUPPORTED_AUDIO = [".wav", ".mp3"]