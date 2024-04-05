import logging, os, re, time
from dotenv import load_dotenv
from spotipy import Spotify, SpotifyClientCredentials
from notion_client import Client

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_API = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
NOTION = Client(auth=NOTION_TOKEN)

def retrieve_album_metadata(album_name):
    try:
        if album_name not in cached_albums:
            results = SPOTIFY_API.search(q='album:' + album_name, type='album', limit=1)
            album = results['albums']['items'][0]
            album_id = re.search(r'album\/([a-zA-Z0-9]+)', album['external_urls']['spotify']).group(1)
            data = {
                'Album': album['name'],
                'Artists': ', '.join([artist['name'] for artist in album['artists']]),
                'Release Date': album['release_date'],
                'Total Tracks': album['total_tracks'], 
                'Cover URL': album['images'][0]['url'],
                'Album ID': album_id,
                'Tracks': [f"{track['track_number']}. {track['name']}" for track in SPOTIFY_API.album_tracks(album['id'])['items']]
            }
            cached_albums[album_name] = data
        return cached_albums[album_name]

    except Exception as e:
        logging.error(f"Error retrieving album metadata for '{album_name}': {str(e)}")
        return None

def update_album_in_notion(album_id, album_name):
    data = retrieve_album_metadata(album_name)
    if not data:
        logging.warning(f'No album found with the name "{album_name}".')
        albums_to_skip.add(album_name)
        return

    try:
        artists = [{'name': artist} for artist in data['Artists'].split(', ')]

        NOTION.pages.update(
            page_id=album_id,
            properties={
                'Album': {'title': [{'text': {'content': data['Album']}}]},
                'Artists': {'multi_select': artists},
                'Release Date': {'date': {'start': data['Release Date']}},
                'Total Tracks': {'number': data['Total Tracks']},
                'Tracks': {'rich_text': [{'text': {'content': '\n'.join(data['Tracks'])}}]},
                'Spotify URL': {'url': f'https://open.spotify.com/album/{data["Album ID"]}'} 
            },
            cover={
                'type': 'external',
                'external': {'url': data['Cover URL']}
            }
        )
        logging.info(f'Album "{album_name}" updated in Notion database.')

    except Exception as e:
        logging.error(f"Error updating album '{album_name}' in Notion database: {str(e)}")

def fetch_and_populate_albums():
    while True:
        try:
            database = NOTION.databases.query(database_id=NOTION_DATABASE_ID)
            for row in database.get('results', []):
                album_id = row['id']
                album_title = row.get('properties', {}).get('Album', {}).get('title', [])
                if not album_title:
                    continue

                album_name = album_title[0]['text']['content']
                if album_name not in processed_albums and album_name not in albums_to_skip:
                    update_album_in_notion(album_id, album_name)
                    processed_albums.add(album_name)

        except Exception as e:
            logging.error(f"An error occurred while fetching and populating albums: {str(e)}")

        time.sleep(10)

if __name__ == '__main__':
    cached_albums = {}  
    processed_albums = set()  
    albums_to_skip = set()
    fetch_and_populate_albums()