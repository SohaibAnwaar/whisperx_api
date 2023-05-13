import json
import tempfile

import fastapi
from pydantic import BaseModel

import whisperx
from transcribe_audio import transcribe_whisperx
from utils import download_mp3_azure, save_results_to_azure

# Create the app object
app = fastapi.FastAPI()


class RequestData(BaseModel):
    """Request model for the API"""
    mp3_url: str
    json_url: str
    ass_url: str


@app.post('/transcribe')
async def transcribe_audio(data: RequestData):
    """API to transcribe the audio with whisperx

    Args:
        data (request): url of the mp3 (wav) file


    """
    audio_path = data.mp3_url
    json_url = data.json_url
    ass_url = data.ass_url
    # Make temporary Folder
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Download mp3 from url
        audio_filename = audio_path.split("/")[-1].split("?")[0]
        audio_path = download_mp3_azure(audio_path, tmpdirname, audio_filename)

        results = transcribe_whisperx(audio_path)
        # Writing to ass file
        writer = whisperx.utils.get_writer("ass", tmpdirname)
        import pdb; pdb.set_trace()
        writer(results, audio_path)


        json_filepath = audio_filename.replace(".mp3", ".json")
        json_filepath = f"{tmpdirname}/{audio_filename}.json"
        # save content in jsonfile
        with open(json_filepath, "w", encoding="utf-8") as outfile:
            json.dump(results["word_segments"], outfile)
        # save json file to azure
        save_results_to_azure(json_url, json_filepath)
        # save ass file to azure
        ass_filepath = audio_filename.replace(".mp3", ".ass")
        ass_filepath = f"{tmpdirname}/{ass_filepath}"
        save_results_to_azure(ass_url, ass_filepath)
    # return status
    return
