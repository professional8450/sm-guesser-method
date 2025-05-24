from enum import Enum


class Genre(Enum):
    hiphop = 'Hip-Hop'
    pop = 'Pop'
    indie = 'Indie'
    rnb = 'R&B'
    rock = 'Rock'
    kpop = 'K-Pop'


class Members(Enum):
    solo = 'Solo'
    group = 'Group'


class Gender(Enum):
    male = 'Male'
    female = 'Female'
    mixed = 'Mixed'
