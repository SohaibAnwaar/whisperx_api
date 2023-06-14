
import os
from pathlib import Path
import requests
import mimetypes
from azure.storage.blob import ContentSettings
from google.oauth2 import service_account
from google.cloud import storage


def download_mp3_azure(url, tmpdirname, audio_filename):
    """Download mp3 file from azure blob storage

    Args:
        url (_type_): azure blob url of the mp3 file
        tmpdirname (_type_): temporary directory to save the mp3 file
    """
    response = requests.get(url, timeout=30)
    destination = f"{tmpdirname}/{audio_filename}"

    # Save the MP3 file locally
    with open(destination, "wb") as file:
        file.write(response.content)

    return destination


def save_results_to_azure(sas_url,  ass_filepath):
    """Store results back into azure

    Args:
        sas_url (_type_): SAS url to upload audio
        ass_filepath (_type_): ass file path
    """
    file_name_only = os.path.basename(ass_filepath)
    try:
        file_ext = '.' + file_name_only.split('.')[1]
        file_ext = '.txt' if file_ext != ".json" else file_ext
    except IndexError:
        file_ext = None
    # Set content Type
    if file_ext is not None:
        content_type_string = ContentSettings(
            content_type=mimetypes.types_map[".txt"])
    else:
        content_type_string = None
    # Read the file content

    headers = {
        'content-type': content_type_string.content_type,
        'x-ms-blob-type': 'BlockBlob'
    }
    params = {'file': ass_filepath}

    with open(ass_filepath, "rb") as file:
        file_content = file.read()

    # Upload the file using the SAS URL

    response = requests.put(sas_url,
                            data=file_content,
                            headers=headers,
                            params=params,
                            timeout=60)

    # Check if the upload was successful
    if response.status_code == 201:
        print("File uploaded successfully.")
    else:
        print(
            f"Failed to upload the file. Status code: {response.status_code}")



def download_mp3_gcp(url, tmpdirname, audio_filename):
    """
    Download mp3 file from Google Cloud Storage

    Args:
        bucket_name (str): GCS bucket name containing the mp3 file
        blob_name (str): GCS blob name of the mp3 file
        tmpdirname (str): temporary directory to save the mp3 file
        audio_filename (str): name of the audio file to be saved
    """
    blob_name = url.replace("https://storage.googleapis.com/chopcast_staging_bucket/", "")

    bucket_name = 'chopcast_staging_bucket'

    credentials = service_account.Credentials.from_service_account_file('/Users/sohaib/Documents/whisperx_api/chopcast.json')
    destination = f"./data/{audio_filename}"

    # Download the MP3 file from GCP
    client = storage.Client(credentials=credentials)

    bucket = client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)

    destination_dir = Path(destination).parent
    os.makedirs(destination_dir, exist_ok=True)

    with open(destination, "wb") as file:
        blob.download_to_file(file)

    return destination

def save_results_to_gcp(destination_url, ass_filepath):
    """
    Store results back into Google Cloud Storage
    Args:
        destination_url (str): GCS destination directory URL
        ass_filepath (str): ass file path
    """
    bucket_name = 'chopcast_staging_bucket'

    credentials = service_account.Credentials.from_service_account_file('/Users/sohaib/Documents/whisperx_api/chopcast.json')
    
    file_name_only = os.path.basename(ass_filepath)
    try:
        file_ext = '.' + file_name_only.split('.')[1]
        file_ext = '.txt' if file_ext != ".json" else file_ext
    except IndexError:
        file_ext = None

    # Set content Type
    if file_ext is not None:
        content_type_string = mimetypes.types_map[".txt"]
    else:
        content_type_string = None

    # Read the file content
    with open(ass_filepath, "rb") as file:
        file_content = file.read()

    # Upload the file to GCP
    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket(bucket_name)

    # Concatenate the destination directory URL with the filename
    blob_path = f"{destination_url}/{file_name_only}"

    blob = bucket.blob(blob_path)

    if content_type_string is not None:
        blob.content_type = content_type_string
  
    blob.upload_from_string(file_content)

    print("File uploaded successfully.")



