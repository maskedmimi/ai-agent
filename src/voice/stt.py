"""
src/voice/stt.py

Speech-to-text wrapper around faster-whisper, used by scripts/voice_app.py.

Runs on CPU, not GPU: the GPU is already tight on VRAM with qwen3:8b loaded
via Ollama (see docs/plan_toyota_voice_assistant.md), and whisper "small" is
fast enough on CPU for short push-to-talk utterances. language="fr" is
forced rather than auto-detected, since this assistant only ever expects
French — auto-detection adds latency and can mis-detect on short clips.
"""

from faster_whisper import WhisperModel

MODEL_SIZE = "small"
LANGUAGE = "fr"

_model: WhisperModel | None = None  # lazy-loaded, module-level cache


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe(audio_path: str) -> str:
    """
    Transcribe a French audio file to text.

    Args:
        audio_path (str): Path to the recorded audio file (e.g. the
            filepath produced by Gradio's microphone input).

    Returns:
        str: The transcribed text, stripped of leading/trailing whitespace.
        Empty string if nothing was recognized.
    """
    model = _get_model()
    segments, _info = model.transcribe(audio_path, language=LANGUAGE, beam_size=1)
    return " ".join(segment.text.strip() for segment in segments).strip()
