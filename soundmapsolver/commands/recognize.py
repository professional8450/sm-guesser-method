import io
import os
import tempfile
import pygame
import requests
from ..command import Command

from rich.table import Table
from rich.console import Console
from rich.progress_bar import ProgressBar
from rich.style import Style

pygame.mixer.init()
console = Console()

current_song = None
current_song_file = None

temp_dir = tempfile.gettempdir()


def generate_options_table(matches):
    table = Table(title="Top 10 Matches", title_justify='left')

    table.add_column("Song", justify="left")
    table.add_column("Confidence", justify="left")

    for i, m in enumerate(matches):
        if i != 0:
            label = f"[{i + 1}] {m['artist']} - {m['name']}"
            confidence = f"{m['confidence']}% ({m['exact_matches']} matches)"
        else:
            label = f"[green][{i + 1}] {m['artist']} - {m['name']}[/green]"
            confidence = f"[green]{m['confidence']}% ({m['exact_matches']} matches)[/green]"

        table.add_row(
            label,
            confidence
        )

    return table


def download_audio(url: str):
    temp_file_path = os.path.join(temp_dir, "temp_audio.mp3")

    with requests.get(url, stream=True) as r:
        if r.status_code == 200:
            with open(temp_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return temp_file_path
        else:
            return None


def stop_song():
    global current_song, current_song_file

    if current_song:
        pygame.mixer.music.stop()

        if current_song_file:
            current_song_file.close()

        current_song = None
        current_song_file = None


def play_song(url):
    global current_song, current_song_file

    response = requests.get(url)
    current_song_file = io.BytesIO(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load(current_song_file)
    pygame.mixer.music.play()

    current_song = url


def callback(command: Command, src: str):
    try:
        src, genre = src.split(" ", 1)
    except ValueError:
        return command.solver.print_error('Please provide a valid genre.')

    genre = genre.lower()

    if genre in ('h', 'hip-hop', 'hiphop'):
        genre = 'hiphop'

    if genre in ('p', 'pop'):
        genre = 'pop'

    if genre in ('i', 'indie'):
        genre = 'indie'

    if genre in ('r&b', 'rb', 'rnb'):
        genre = 'rnb'

    if genre in ('r', 'rock'):
        genre = 'rock'

    if genre not in ('hiphop', 'pop', 'indie', 'rnb', 'rock', 'unknown'):
        return command.solver.print_error('Please provide a valid genre.')

    url = f"https://api.soundmap.tools/songGuesser/recognize?genre={genre}"
    boundary = "----geckoformboundary779aea642d0b1072415dbb4021628d1"

    payload = (
        f"{boundary}\r\n"
        'Content-Disposition: form-data; name="url"\r\n'
        "\r\n"
        f"{src}\r\n"
        f"{boundary}--\r\n"
    )

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary[2:]}"
    }

    result = requests.post(url, data=payload.encode(), headers=headers)
    matches = []
    data = result.json().get('matches')

    if not data:
        return command.solver.print_error('No matches found.')

    for match in data:
        matches.append({
            'artist': match['artist']['name'],
            'confidence': int(match['confidence']),
            'exact_matches': int(match['exactMatches']),
            'preview_url': match['preview_url'],
            'name': match['name'],
            'id': match['id']
        })
    matches = sorted(matches, key=lambda item: item['confidence'], reverse=True)

    if len(matches) == 0:
        return command.solver.print_error('No matches found.')

    selected_matches = matches[:10]
    selected_song = selected_matches[0]

    command.solver.call('clear')
    command.solver.console.print(generate_options_table(selected_matches))

    command.solver.print_warning(
        'Type a number [1-10] to play the song. Type "q" to exit this menu. The first song has been copied by default.'
    )

    command.solver._copy_to_clipboard(
        content=f'>>> **"{selected_song['name']}"** (by {selected_song['artist']})!\n'
                f'-# https://open.spotify.com/track/{selected_song["id"]}'
    )
    last_input = None

    while True:
        unmodified_user_input = input(">> ").strip()
        user_input = unmodified_user_input.lower()

        if user_input == 'q':
            command.solver.print_error(content='Exiting.')
            stop_song()
            break

        if user_input.startswith('https') or user_input.startswith('first'):
            return command.solver.call(unmodified_user_input)

        if user_input == 'reset':
            selected_matches = list(sorted(matches, key=lambda item: item['confidence'], reverse=True))[:10]
            selected_song = selected_matches[0]

            command.solver.call('clear')
            command.solver.print_warning(
                'Type a number [1-10] to play the song. Type "q" to exit this menu. The first song has been copied by default.'
            )
            command.solver.console.print(generate_options_table(selected_matches))

        if user_input.startswith('artist '):
            artist = user_input.split(' ')[1]
            selected_matches = list(filter(lambda item: item['artist'].lower().startswith(artist.lower()), sorted(matches, key=lambda item: item['confidence'], reverse=True)))[:10]
            selected_song = selected_matches[0]

            command.solver.call('clear')
            command.solver.print_warning(
                'Type a number [1-10] to play the song. Type "q" to exit this menu. The first song has been copied by default.'
            )
            command.solver.console.print(generate_options_table(selected_matches))

        if user_input.startswith('song '):
            artist = user_input.split(' ')[1]
            selected_matches = list(filter(lambda item: item['name'].lower().startswith(artist.lower()), sorted(matches, key=lambda item: item['confidence'], reverse=True)))[:10]
            selected_song = selected_matches[0]

            command.solver.call('clear')
            command.solver.print_warning(
                'Type a number [1-10] to play the song. Type "q" to exit this menu. The first song has been copied by default.'
            )
            command.solver.console.print(generate_options_table(selected_matches))

        elif user_input == 'stop' or user_input == 's':
            stop_song()

        elif user_input.isdigit() and 1 <= int(user_input) <= 10:
            song_index = int(user_input) - 1
            selected_song = selected_matches[song_index]

            command.solver.print_success(
                content=f'Playing: "{selected_song["name"]}". Type stop to end playing, or quit to exit the menu.')
            command.solver._copy_to_clipboard(
                content=f'>>> **"{selected_song['name']}"** (by {selected_song['artist']})\n'
                        f'-# https://open.spotify.com/track/{selected_song["id"]}'
            )

            play_song(selected_song['preview_url'])

        elif user_input == 'copy':
            command.solver.print_success(content=f'Copying {selected_song["name"]}.')
            command.solver._copy_to_clipboard(
                content=f'>>> **"{selected_song['name']}"** (by {selected_song['artist']})!\n'
                        f'-# https://open.spotify.com/track/{selected_song["id"]}'
            )
            break

        elif user_input == "r" and last_input is not None:
            return command.solver.call(last_input)

        else:
            last_input = user_input
            command.solver.print_error(content='Invalid input. Type "q" to exit, or "r" to exit and run the command you just entered.')


command = Command(
    name='recognize',
    description='',
    usage='',
    callback=callback,
    no_split=False
)

__all__ = ['command']
