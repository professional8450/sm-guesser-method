from .artist import Artist
from datetime import datetime
from typing import Optional


class History(object):
    def __init__(self, *, recommended_guess: 'Artist', query: str, inferred_first_guess: Optional['Artist'] = None):
        self.timestamp: datetime = datetime.now()
        self.recommended_guess = recommended_guess
        self.query = query
        self.inferred_first_guess = inferred_first_guess
