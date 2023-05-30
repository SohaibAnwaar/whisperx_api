import whisperx_local as whisperx
import whisper


def transcribe_whisperx(audio_path: str, model_path:str = "small"):
    """Transcribtion with the help of whisper

    Args:
        audio_path (str): audio file path

    Returns:
        json: word level transcription
    """

    device = "cuda"

    # transcribe with original whisper
    model = whisper.load_model(model_path, device)
    result = model.transcribe(audio_path)

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device)

    # align whisper output
    result_aligned = whisperx.align(
        result["segments"], model_a, metadata, audio_path, device)
    return result_aligned
