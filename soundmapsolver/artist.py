from .enums import Members, Genre, Gender


class Artist(object):
    def __init__(self, **kwargs):
        self.name: str = kwargs['name']
        self.members: Members = Members(kwargs['type'].title())
        self.genre: Genre = Genre(kwargs['genre'].title())
        self.type: Members = self.members
        self.popularity: int = int(kwargs['popularity'])
        self.debut: int = int(kwargs['debut'])
        self.country: str = kwargs['country']
        self.gender: Gender = Gender(kwargs['gender'].title())
        self.ranks = None
        self.score: float = 0
        self.alt: float = 0
        if kwargs.get('rank_2'):
            self.ranks = (
                int(kwargs['rank_2']),
                int(kwargs['rank_3']),
                int(kwargs['rank_4']),
                int(kwargs['rank_5_or_more'])
            )

    def __str__(self):
        return f"<Artist name='{self.name}' popularity={self.popularity} debut={self.debut}>"

    def __repr__(self):
        return self.__str__()

    def set_score(self, score: float):
        self.score = score

    def set_alt(self, score: float):
        self.alt = score
