import reflex as rx
from faster_whisper import WhisperModel
import logging
from pathlib import Path

MODEL_SIZE = "small.en"
model: WhisperModel | None = None


def get_model() -> WhisperModel | None:
    """Loads the Whisper model, caching it in a global variable."""
    global model
    if model is None:
        try:
            logging.info(f"Loading faster-whisper model: {MODEL_SIZE}...")
            model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.exception(f"Failed to load Whisper model '{MODEL_SIZE}': {e}")
            return None
    return model


def transcribe_audio(audio_path: Path) -> str | None:
    """Transcribes an audio file using the pre-loaded Whisper model."""
    whisper_model = get_model()
    if whisper_model is None:
        logging.error("Transcription failed because Whisper model is not available.")
        return None
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        logging.warning(f"Audio file does not exist or is empty: {audio_path}")
        return ""
    try:
        logging.info(f"Starting transcription for {audio_path}...")
        segments, _ = whisper_model.transcribe(audio_path, beam_size=5, language="en")
        transcript = " ".join([segment.text for segment in segments])
        logging.info(f"Transcription successful for {audio_path}.")
        return transcript.strip()
    except Exception as e:
        logging.exception(f"Error during audio transcription for {audio_path}: {e}")
        return None