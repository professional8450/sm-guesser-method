from ..command import Command
from ..artist import Artist


def callback(command: Command, search: str):
    if not command.solver.first_guesses:
        return command.solver.print_error('This command is disabled.')

    artist = None
    if len(search) == 4 and search.isdigit():  # Debut
        artist = next(
            filter(lambda item: item.artist.debut == int(search) and item.attribute == 'debut',
                   command.solver.first_guesses), None
        )

    if len(search) <= 3 and search.isdigit():  # Popularity
        artist = next(
            filter(lambda item: item.artist.popularity == int(search) and item.attribute == 'popularity',
                   command.solver.first_guesses), None
        )

    if search in ('s', 'g'):  # Solo/group
        artist = next(
            filter(lambda item: item.artist.members == command.solver._enum_from_first_letter(enum_class='members',
                                                                                              prefix=search) and item.attribute == 'members',
                   command.solver.first_guesses), None
        )

    if search in ('m', 'f', 'mx'):  # Gender
        artist = next(
            filter(lambda item: item.artist.gender == command.solver._enum_from_first_letter(enum_class='gender',
                                                                                             prefix=search) and item.attribute == 'gender',
                   command.solver.first_guesses), None
        )

    if search in ('r', 'h', 'rb', 'p', 'i'):  # Genre
        artist = next(
            filter(lambda item: item.artist.genre == command.solver._enum_from_first_letter(enum_class='genre',
                                                                                            prefix=search) and item.attribute == 'genre',
                   command.solver.first_guesses), None
        )

    if len(search) == 2 and search not in ('h', 'p', 'r', 'rb', 'i', 'mx') and not search.isdigit():  # Country
        artist = next(
            filter(lambda item: item.artist.country == search.upper() and item.attribute == 'country',
                   command.solver.first_guesses), None
        )

    if not artist:
        return command.solver.print_error(
            artist.artist.name if artist else 'Sorry, but I think you typed it incorrectly.')

    command.solver._copy_to_clipboard(
        f'The best starting guess for your hint `({artist.value} {artist.attribute.lower()})` is **{artist.artist.name}**!'
    )

    command.solver.print_success(f'{artist.value} {artist.attribute.lower()} = {artist.artist.name}')
    return None


command = Command(
    name='first',
    description='Shows you the best first guess for a specific hint. Uses the same format as the solver.',
    usage='first',
    callback=callback
)

__all__ = ['command']
