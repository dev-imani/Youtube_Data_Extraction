import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_Key = os.getenv("API_Key")
Channel_HANDLER = "MrBeast"
maxResults = 50


def get_playList_id():
    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={Channel_HANDLER}&key= {API_Key}"

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

# print(json.dumps(data,indent=4))
        channel_items = data['items'][0]

        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlistId)
        return channel_playlistId
    except requests.exceptions.RequestException as e:
        raise e


def get_video_id(playlist_id):
    video_ids = []
    pageToken = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_id}&key={API_Key}"
    print(f"Getting videos from playlist: {playlist_id}")
    try:
        while True:
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()



            for items in data.get('items', []):
                video_id = items['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
       
        raise e


if __name__ == "__main__":
    playlist_id = get_playList_id()
    
    print( get_video_id(playlist_id))
