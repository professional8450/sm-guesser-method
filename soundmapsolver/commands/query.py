import re
from ..command import Command
from ..artist import Artist


def callback(command: Command, query: str):
    if '+' in query:
        spl = query.split(" + ")
        if len(spl) >= 2:
            previous = spl[0]
            query = spl[1]

            entry = command.solver._get_from_history(previous)
            if entry:
                query = f'{entry.query} + {query}'

    query = re.sub(r'\(.*?\)', '', query).strip()
    rules = command.solver._build_rules(query)
    if not rules:
        return []

    artists = command.solver._get_passing_artists(rules=rules)
    command.solver._print_artists(artists=artists, title=f'Artists that fit:', query=query, rules=rules)


command = Command(
    name='query',
    description='Shows options based on a given query. Default command unless a link is provided',
    usage="2012v 1999vy 147vy 193^y !us gb iey m s",
    callback=callback
)

__all__ = ['command']
