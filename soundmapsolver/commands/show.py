from ..command import Command
from ..artist import Artist


def callback(command: Command, artist: Artist):
    print()
    command.solver._print_artists(artists=[artist], title=f"{artist.name}'s statistics")
    command.solver._print_odds_panel(artist=artist)


command = Command(
    name='show',
    description='Shows the stats of a given artist.',
    usage='show <artist name>',
    callback=callback
)

__all__ = ['command']
