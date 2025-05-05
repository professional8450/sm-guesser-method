from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from soundmapsolver import Solver


class Guess:
    def __init__(self, *, attribute: str, value: str, artist: str, solver: 'Solver'):
        self.attribute = attribute
        self.value = value
        self.artist = solver._search(artist)[0]
