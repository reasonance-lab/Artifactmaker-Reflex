import reflex as rx
from typing import Literal
import datetime
from app import classes, storage, transcription
import logging
from pathlib import Path


class RecorderState(rx.State):
    selected_class_slug: str = list(classes.CLASS_INFO.keys())[0]
    entry_date: str = datetime.date.today().isoformat()
    typed_text: str = ""
    image_files: list[str] = []
    video_files: list[str] = []
    audio_file: str | None = None
    recording_status: Literal["idle", "recording", "processing", "error"] = "idle"
    transcript: str = ""

    @rx.var
    def selected_class_info(self) -> classes.ClassInfo:
        return classes.CLASS_INFO[self.selected_class_slug]

    @rx.var
    def accent_color(self) -> str:
        return self.selected_class_info["accent_color"]

    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        self.image_files = []
        for file in files:
            upload_data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / file.name
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.image_files.append(file.name)
        if self.image_files:
            yield rx.toast.success(f"{len(self.image_files)} image(s) selected.")

    @rx.event
    async def handle_video_upload(self, files: list[rx.UploadFile]):
        self.video_files = []
        for file in files:
            upload_data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / file.name
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.video_files.append(file.name)
        if self.video_files:
            yield rx.toast.success(f"{len(self.video_files)} video(s) selected.")

    def _reset_inputs(self):
        self.entry_date = datetime.date.today().isoformat()
        self.typed_text = ""
        self.image_files = []
        self.video_files = []
        self.audio_file = None
        self.transcript = ""
        self.recording_status = "idle"
        yield rx.clear_selected_files("image_upload")
        yield rx.clear_selected_files("video_upload")
        return

    async def _get_upload_files(self, filenames: list[str]) -> list[rx.UploadFile]:
        upload_dir = rx.get_upload_dir()
        files = []
        for filename in filenames:
            file_path = upload_dir / filename
            if file_path.exists():
                files.append(rx.UploadFile(name=filename, data=file_path.read_bytes()))
        return files

    @rx.event
    async def save_entry_event(self):
        image_uploads = await self._get_upload_files(self.image_files)
        video_uploads = await self._get_upload_files(self.video_files)
        audio_upload = (
            (await self._get_upload_files([self.audio_file]))[0]
            if self.audio_file
            else None
        )
        try:
            success = storage.save_entry(
                class_slug=self.selected_class_slug,
                date_str=self.entry_date,
                images=image_uploads,
                videos=video_uploads,
                audio_file=audio_upload,
                typed_text=self.typed_text,
                transcript=self.transcript,
            )
            if success:
                yield rx.toast.success("Entry saved successfully!")
                for event in self._reset_inputs():
                    yield event
            else:
                yield rx.toast.error("Failed to save entry. Please try again.")
        except Exception as e:
            logging.exception(f"Error in save_entry_event: {e}")
            yield rx.toast.error("An unexpected error occurred.")

    @rx.event
    def start_recording(self):
        self.recording_status = "recording"
        yield
        yield rx.call_script("startRecording()")

    @rx.event
    def stop_recording(self):
        self.recording_status = "processing"
        yield
        yield rx.call_script("stopRecording()")

    @rx.event(background=True)
    async def process_audio_and_transcribe(self, audio_blob: rx.UploadFile):
        try:
            async with self:
                self.audio_file = None
                self.transcript = ""
                audio_data = await audio_blob.read()
                filename = (
                    f"recording_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
                )
                upload_dir = rx.get_upload_dir()
                upload_dir.mkdir(parents=True, exist_ok=True)
                file_path = upload_dir / filename
                with file_path.open("wb") as f:
                    f.write(audio_data)
                self.audio_file = filename
                yield
            transcript_result = transcription.transcribe_audio(Path(file_path))
            async with self:
                if transcript_result is not None:
                    self.transcript = transcript_result
                    self.recording_status = "idle"
                    yield rx.toast.success("Audio processed and transcribed!")
                else:
                    self.transcript = ""
                    self.recording_status = "error"
                    yield rx.toast.error("Transcription failed.")
        except Exception as e:
            logging.exception(f"Error processing audio: {e}")
            async with self:
                self.recording_status = "error"
                yield rx.toast.error("An error occurred during audio processing.")