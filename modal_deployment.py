"""Deploy whisperx with modal deployment
"""
import json
import sys
import tempfile

import modal
from modal import web_endpoint

from utils import download_mp3_azure, save_results_to_azure

LOCAL_CODE_PATH = "/home/sohaib/Documents/chopcast_workspace/whisperx_api/"
REMOTE_PATH = "/tmp/models/"

sys.path.append(REMOTE_PATH)


stub = modal.Stub(name="whisperx")

# whisperx_docker = modal.Image.from_dockerfile("Dockerfile")
whisperx_docker = modal.Image.from_dockerhub("sohaibanwaar/whisperx:latest")

@stub.function(gpu="any", image=whisperx_docker,
 mounts=[modal.Mount.from_local_dir(LOCAL_CODE_PATH, remote_path=REMOTE_PATH)])
@web_endpoint(label="whisperx")
def transcribe_audio_large(audio_url, destination_url):
    """API to transcribe the audio with whisperx

    Args:
        audio_url (request): url of the mp3 (wav) file
        destination_url (request): url of the json file to save the results

    """
    # pylint: disable=import-outside-toplevel
    from transcribe_audio import transcribe_whisperx
    # Make temporary Folder
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Download mp3 from url
        audio_filename = audio_url.split("/")[-1].split("?")[0]
        audio_url = download_mp3_azure(audio_url, tmpdirname, audio_filename)
        # Transcribing with WhisperX f"{REMOTE_PATH}models/small.pt"
        results = transcribe_whisperx(audio_url, model_path="large")   
        json_filepath = audio_filename.replace(".mp3", ".json")
        json_filepath = f"{tmpdirname}/{audio_filename}.json"
        # save content in jsonfile
        with open(json_filepath, "w", encoding="utf-8") as outfile:
            json.dump(results["word_segments"], outfile)
        # save json file to azure
        save_results_to_azure(destination_url, json_filepath)

    return destination_url
