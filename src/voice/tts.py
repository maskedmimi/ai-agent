"""
src/voice/tts.py

Text-to-speech wrapper around Piper, used by scripts/voice_app.py. Uses
Piper's Python API directly (no external `piper` binary needed) with a
locally downloaded French voice model.

Voice model: data/voices/fr_FR-siwis-medium.onnx (+ .onnx.json), downloaded
via:
    python -m piper.download_voices --download-dir data/voices fr_FR-siwis-medium
"""

import tempfile
import wave
from pathlib import Path

from piper import PiperVoice

VOICE_PATH = Path("data/voices/fr_FR-siwis-medium.onnx")

_voice: PiperVoice | None = None  # lazy-loaded, module-level cache


def _get_voice() -> PiperVoice:
    global _voice
    if _voice is None:
        if not VOICE_PATH.exists():
            raise FileNotFoundError(
                f"No Piper voice model found at {VOICE_PATH}. Download it with:\n"
                f"  python -m piper.download_voices --download-dir data/voices fr_FR-siwis-medium"
            )
        _voice = PiperVoice.load(str(VOICE_PATH))
    return _voice


def synthesize(text: str) -> str:
    """
    Synthesize French speech from text.

    Args:
        text (str): The text to speak.

    Returns:
        str: Path to a temporary .wav file containing the synthesized
        speech. Caller is responsible for the file afterwards (e.g.
        handing its path to a Gradio Audio output).
    """
    voice = _get_voice()
    fd, path = tempfile.mkstemp(suffix=".wav")
    with wave.open(path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    return path
