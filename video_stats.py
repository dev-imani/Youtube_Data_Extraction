import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

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


def extract_video_data(video_ids):
    extracted_data = []

    def batch_lists(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id:video_id+batch_size]

    try:
        for batch in batch_lists(video_ids, maxResults):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=statistics,snippet,contentDetails&id={video_ids_str}&key={API_Key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                contentDetails = item.get('contentDetails', {})

                video_data = {
                    'video_id': video_id,
                    'title': snippet.get('title', 'N/A'),
                    'publishedAt': snippet.get('publishedAt', 'N/A'),
                    'duration': contentDetails.get('duration', 'N/A'),
                    'view_count': statistics.get('viewCount', None),
                    'like_count': statistics.get('likeCount', None),
                    'comment_count': statistics.get('commentCount', None)
                }
                extracted_data.append(video_data)

        return extracted_data
    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):
    file_path =f"./data/YT_data_{date.today()}.json"

    with open(file_path,"w",encoding="utf-8") as json_outfile:
        json.dump(extracted_data,json_outfile,indent=4,ensure_ascii=False)


if __name__ == "__main__":
    playlist_id = get_playList_id()
    video_ids = get_video_id(playlist_id)
    video_data =extract_video_data(video_ids)
    save_to_json(video_data)
