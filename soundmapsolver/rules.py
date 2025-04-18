from abc import ABC
from enum import Enum
from typing import Callable, Union, List
from .artist import Artist


class Rule(ABC):
    def __init__(self, *, attribute: str, check: Callable[[Artist], bool]):
        self.attribute: str = attribute
        self.check: Callable[[Artist], bool] = check
        self._original_value = None

    def __call__(self, artist: Artist) -> bool:
        return self.check(artist)


class ExactRule(Rule):
    def __init__(self, *, attribute: str, value: Union[str, int, Enum]):
        self.value = value
        super().__init__(
            attribute=attribute,
            check=lambda artist: getattr(artist, self.attribute) == self.value
        )


class InRule(Rule):
    def __init__(self, *, attribute: str, values: List[Union[str, int, Enum]]):
        self.values = values
        super().__init__(
            attribute=attribute,
            check=lambda artist: getattr(artist, self.attribute) in self.values
        )


class ExclusionRule(Rule):
    def __init__(self, *, attribute: str, values: List[Union[str, int, Enum]]):
        self.values = values
        super().__init__(
            attribute=attribute,
            check=lambda artist: getattr(artist, self.attribute) not in self.values
        )


class WithinRule(Rule):
    def __init__(self, *, attribute: str, min: int, max: int):
        self.min = min
        self.max = max
        super().__init__(
            attribute=attribute,
            check=lambda artist: self.min < getattr(artist, self.attribute) < self.max
        )
