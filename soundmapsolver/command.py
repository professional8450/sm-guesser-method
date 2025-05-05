import inspect
from .artist import Artist
from typing import Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .solver import Solver


class Command(object):
    def __init__(self, *, name: str, description: str, usage: str, callback: Callable, alias: List[str] = None, no_split: bool = True):
        self.name = name
        self.description = description
        self.usage = usage
        self.callback = callback
        self.solver: Optional[Solver] = None
        self.aliases: List[str] = alias or []
        self.no_split: bool = True

    def init(self, solver: 'Solver'):
        self.solver = solver

    def run(self, arguments: List[str]):
        signature = inspect.signature(self.callback)
        params = list(signature.parameters.values())

        if len(params) == 1:
            return self.callback(self)

        if len(params) == 2 and self.no_split:
            arguments = " ".join(arguments)

        if len(params) == 2 and params[1].annotation is Artist:
            artist: List[Artist] = self.solver._search(arguments)
            if len(artist) == 0:
                return self.solver.print_error('Could not find an artist with that name.')
            arguments = artist[0]

        if len(params) == 3 and params[1].annotation is Artist and params[2].annotation is Artist:
            arguments = " ".join(arguments)
            arguments = arguments.split(", ")
            if len(arguments) < 2:
                return self.solver.print_error('Artist names must be split with a comma symbol.')

            artist_a = self.solver._search(arguments[0])
            artist_b = self.solver._search(arguments[1])
            if (not artist_a) or (not artist_b):
                return self.solver.print_error('Could not find an artist with that name.')
            return self.callback(self, artist_a[0], artist_b[0])

        self.callback(self, arguments)
