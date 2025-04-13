"""Before running this script, ensure that you have added the id's you're going to use in the test users
for Spotify and YouTube!!!"""


from requests.exceptions import HTTPError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from spotipy import Spotify
from spotipy.oauth2 import SpotifyPKCE
from dotenv import load_dotenv
import os

load_dotenv()


sp = Spotify(auth_manager=SpotifyPKCE(
    client_id=os.getenv("CLIENT_ID"),
    redirect_uri=os.getenv("REDIRECT_URI"),  # still needed here
    scope="playlist-read-private"
))

def get_playlist_tracks(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(f"{track['name']} {track['artists'][0]['name']}")
    return tracks


# Authenticate and create service
scopes = ["https://www.googleapis.com/auth/youtube"]
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
credentials = flow.run_local_server(port=8080)
youtube = build("youtube", "v3", credentials=credentials)

def search_youtube(query):
    try:
        q = f"{query} topic"
        request = youtube.search().list(
            part="snippet",
            q=q,
            type="video",
            maxResults=1
        )
        response = request.execute()
        return response['items'][0]['id']['videoId'] if response['items'] else None
    except HTTPError:
        print(f"{query} not found.")

def create_youtube_playlist(title, description=""):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "private"}
        }
    )
    response = request.execute()
    return response['id']

def add_video_to_playlist(playlist_id, video_id):
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()


spotify_playlist_id = "add your own id bro"
tracks = get_playlist_tracks(spotify_playlist_id)

yt_playlist_id = create_youtube_playlist("youtube playlist name")

for track in tracks:
    video_id = search_youtube(track)
    if video_id:
        add_video_to_playlist(yt_playlist_id, video_id)
