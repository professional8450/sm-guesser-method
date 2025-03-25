from .artist import Artist
from datetime import datetime


class History(object):
    def __init__(self, *, recommended_guess: 'Artist', query: str):
        self.timestamp: datetime = datetime.now()
        self.recommended_guess = recommended_guess
        self.query = query
