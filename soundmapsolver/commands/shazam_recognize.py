import time

import requests

from rich import print as rich_print
from rich.syntax import Syntax

from ..command import Command
from ..artist import Artist

import subprocess
import os


import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_apple_music_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    # Keep only the 'i' parameter
    clean_query = urlencode({'i': query['i'][0]}) if 'i' in query else ''
    # Reconstruct the URL
    cleaned_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', clean_query, ''))
    return cleaned_url.replace('intent://', 'https://')

def extract_shazam_data(data):

    if not (data.get('track')):
        return {}
    song_name = (data['track']['title'])
    artist_name = (data['track']['subtitle'])
    album_name = (next((item['text'] for item in data['track']['sections'][0]['metadata'] if item['title'] == 'Album')))
    apple_url = next(
        (action["uri"]
         for option in data['track']['hub'].get("options", [])
         for action in option.get("actions", [])
         if action.get("type") == "applemusicopen" or action.get('type') is None or action.get("name") == 'hub:applemusic:deeplink'),
        None
    )

    return {
        'apple_song_url': clean_apple_music_url(apple_url) if apple_url else '',
        'artist_name': artist_name,
        'song_name': song_name,
        'album_name': album_name
    }



def download_mov(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def convert_mov_to_mp3(input_path, output_path):
    subprocess.run([
        "ffmpeg",
        "-i", input_path,
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def callback(command: Command, url: str):
    start = time.time()

    # data = {
   #     'url': url,
   #     'return': 'spotify',
   #     'api_token': '53eccc4733678d5aa028df5b7820c86c'
   # }
   # result = requests.post('https://api.audd.io/', data=data)

    download_mov(url, 'temp.mov')
    convert_mov_to_mp3('temp.mov', 'temp.mp3')
    url = "https://shazam-song-recognition-api.p.rapidapi.com/recognize/file"
    file_path = "temp.mp3"

    headers = {
       "x-rapidapi-key": "32d40c8eb4msha0887a51ca532fep191a6ejsn29ff2704b1ae",
       "x-rapidapi-host": "shazam-song-recognition-api.p.rapidapi.com",
       "Content-Type": "application/octet-stream"
    }

    with open(file_path, "rb") as f:
       file_data = f.read()

    result = requests.post(url, headers=headers, data=file_data)
    os.remove('temp.mp3')

    if result.status_code == 200:
        json_result = result.json()
        data = extract_shazam_data(json_result)

        if data:
            artist = data.get('artist_name', '?')
            title = data.get('song_name', '?')
            album = data.get('album_name', '?')
            link = data.get('apple_song_url', '?')

            command.solver._copy_to_clipboard(content=f'The song is most likely **"{title}"** (by {artist}), from the album "{album}"!\n{link}\n\n'
                                                      f'-# Solved in {(time.time() - start):.2f}s. I recommend listening to the linked song to make sure.')
            command.solver.print(text_color='green', content=f'The song is most likely "{title}" by {artist}, from the album "{album}"!')
        else:
            command.solver.print_error('I don\'t know!')
    else:
        command.solver.print_error(f"Request failed with status code {result.status_code}")
        json_str = json.dumps(result.json(), indent=4, sort_keys=True)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        rich_print(syntax)


command = Command(
    name='shazam',
    description='',
    usage='',
    callback=callback
)

__all__ = ['command']
