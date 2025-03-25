import os
from ..command import Command
from ..artist import Artist


def callback(command: Command):
    print("\033c")
    os.system('cls' if os.name == 'nt' else 'clear')


command = Command(
    name='clear',
    description='Clears the console.',
    usage='clear',
    callback=callback
)

__all__ = ['command']
