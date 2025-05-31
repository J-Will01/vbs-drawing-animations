import os
import io
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from tqdm import tqdm

# Replace this with your Google Drive folder ID
FOLDER_ID = '1v6vPHLL9CwzomIrLxr2fHwVd2FfbdzAP'

link_to_folder = 'https://drive.google.com/drive/u/0/folders/1v6vPHLL9CwzomIrLxr2fHwVd2FfbdzAP'

# Target directory to save images
DOWNLOAD_DIR = './downloaded_images'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def list_image_files(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    files = []
    page_token = None
    while True:
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, mimeType)',
                                        pageToken=page_token).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files

def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    filepath = os.path.join(DOWNLOAD_DIR, file_name)
    with open(filepath, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    return filepath

def download_images():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    print("Fetching image files...")
    files = list_image_files(service, FOLDER_ID)

    if not files:
        print("No images found in the folder.")
        return

    print(f"Found {len(files)} image files. Downloading...")

    for file in tqdm(files):
        file_name = file['name']
        file_id = file['id']
        download_file(service, file_id, file_name)

    print("Download complete!")

if __name__ == '__main__':
    download_images()