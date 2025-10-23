import reflex as rx
from typing import Any, TypedDict
import logging
from app import classes, utils, storage


class EntryData(TypedDict, total=False):
    images: list[str]
    videos: list[str]
    audio_path: str | None
    typed_text: str
    transcript: str


class GalleryState(rx.State):
    selected_class_slug: str = ""
    available_dates: list[str] = []
    current_date_index: int = -1
    current_entry: EntryData = {
        "images": [],
        "videos": [],
        "audio_path": None,
        "typed_text": "",
        "transcript": "",
    }

    @rx.event
    def on_load(self):
        slug = self.router.page.params.get("class", list(classes.CLASS_INFO.keys())[0])
        if slug in classes.CLASS_INFO:
            self.selected_class_slug = slug
        else:
            self.selected_class_slug = list(classes.CLASS_INFO.keys())[0]
        logging.info(f"Gallery on_load triggered for class: {self.selected_class_slug}")
        return GalleryState.load_dates_for_class

    @rx.event(background=True)
    async def load_dates_for_class(self):
        async with self:
            self.available_dates = sorted(
                utils.get_all_dates_for_class(self.selected_class_slug), reverse=True
            )
            if self.available_dates:
                self.current_date_index = 0
            else:
                self.current_date_index = -1
        if self.current_date_index != -1:
            yield GalleryState.load_entry_for_date

    @rx.event
    async def load_entry_for_date(self):
        if self.current_date_index < 0 or self.current_date_index >= len(
            self.available_dates
        ):
            self.current_entry = {
                "images": [],
                "videos": [],
                "audio_path": None,
                "typed_text": "",
                "transcript": "",
            }
            return
        date_str = self.available_dates[self.current_date_index]
        entry_data = storage.load_entry(self.selected_class_slug, date_str)
        self.current_entry = self._process_entry_data(entry_data)

    def _process_entry_data(self, entry_data):
        if not entry_data:
            return {
                "images": [],
                "videos": [],
                "audio_path": None,
                "typed_text": "",
                "transcript": "",
            }
        processed: EntryData = {
            "images": [],
            "videos": [],
            "audio_path": None,
            "typed_text": "",
            "transcript": "",
        }
        for key, value in entry_data.items():
            if isinstance(value, list) and value and hasattr(value[0], "as_posix"):
                processed[key] = [p.as_posix().replace("data/", "") for p in value]
            elif hasattr(value, "as_posix"):
                processed[key] = (
                    value.as_posix().replace("data/", "") if value else None
                )
            else:
                processed[key] = value
        return processed

    @rx.var
    def selected_class_info(self) -> classes.ClassInfo:
        return classes.CLASS_INFO.get(
            self.selected_class_slug, list(classes.CLASS_INFO.values())[0]
        )

    @rx.var
    def accent_color(self) -> str:
        return self.selected_class_info["accent_color"]

    @rx.var
    def has_entries(self) -> bool:
        return len(self.available_dates) > 0

    @rx.var
    def total_dates(self) -> int:
        return len(self.available_dates)

    @rx.var
    def current_date(self) -> str:
        if 0 <= self.current_date_index < len(self.available_dates):
            return self.available_dates[self.current_date_index]
        return ""

    @rx.event
    def set_current_date(self, date_str: str):
        try:
            self.current_date_index = self.available_dates.index(date_str)
            return GalleryState.load_entry_for_date
        except ValueError as e:
            logging.exception(f"Date {date_str} not found in available dates: {e}")

    @rx.event
    def next_date(self):
        if self.current_date_index < len(self.available_dates) - 1:
            self.current_date_index += 1
            return GalleryState.load_entry_for_date

    @rx.event
    def prev_date(self):
        if self.current_date_index > 0:
            self.current_date_index -= 1
            return GalleryState.load_entry_for_date