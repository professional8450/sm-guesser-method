from rich.panel import Panel
from rich.table import Table

from ..command import Command
from ..artist import Artist


def callback(command: Command, start: Artist, end: Artist):
    history = command.solver._calculate_path(start=start, end=end)

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Next guess", justify="left")
    table.add_column("Remaining options", justify="left")

    how_many_guesses = len(history)
    last_entry = history[-1]
    if isinstance(last_entry[0], list):
        how_many_guesses = f"{len(history)}-{len(history) + 1}"

    for entry in history:
        artist = entry[0]
        remaining = entry[1] if entry[1] is not None else "-"
        if isinstance(artist, list):
            artist_names = " or ".join(a.name for a in artist)
        else:
            artist_names = artist.name

        if entry == history[len(history) - 1]:
            table.add_row(f'[green]{artist_names}[/]', "-")
        else:
            odds = (1/remaining) * 100
            if odds == 100.0:
                odds = ''
            else:
                odds = f'({odds:.1f}% chance)'

            table.add_row(artist_names, f'{str(remaining)} {odds}')

    panel = Panel(table, title=f"Path from {start.name} to {end.name}", subtitle=f"({how_many_guesses} guesses)", expand=False)
    command.solver.console.print(panel)


command = Command(
    name='path',
    description='Shows the path that will be taken between two artists.',
    usage='path <artist>, <artist>',
    callback=callback
)

__all__ = ['command']
