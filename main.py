import json
import tempfile

import fastapi
from pydantic import BaseModel

import whisperx_local as whisperx
from transcribe_audio import transcribe_whisperx
from utils import download_mp3_azure, save_results_to_azure

# Create the app object
app = fastapi.FastAPI()


class RequestData(BaseModel):
    """Request model for the API"""
    audio_url: str
    destination_url: str


@app.post('/transcribe')
async def transcribe_audio(data: RequestData):
    """API to transcribe the audio with whisperx

    Args:
        data (request): url of the mp3 (wav) file


    """
    audio_path = data.audio_url
    destination_url = data.destination_url
    # Make temporary Folder
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Download mp3 from url
        audio_filename = audio_path.split("/")[-1].split("?")[0]
        audio_path = download_mp3_azure(audio_path, tmpdirname, audio_filename)
        # Transcribing with WhisperX
        results = transcribe_whisperx(audio_path, model_path="./models/small.pt")   
        json_filepath = audio_filename.replace(".mp3", ".json")
        json_filepath = f"{tmpdirname}/{audio_filename}.json"
        # save content in jsonfile
        with open(json_filepath, "w", encoding="utf-8") as outfile:
            json.dump(results["word_segments"], outfile)
        # save json file to azure
        save_results_to_azure(destination_url, json_filepath)
    # return status
    return True
