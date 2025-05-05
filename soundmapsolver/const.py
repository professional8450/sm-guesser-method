import sys
from .enums import Members, Genre, Gender

AMERICA = ('US', 'CA', 'MX', 'BB')
EUROPE = ('FR', 'DE', 'GB', 'NO', 'BE', 'DK', 'ES', 'IE', 'IT', 'NL', 'PL', 'RO', 'SE', 'UA')
OCEANIA = ('AU', 'NZ')
LATIN = ('BR', 'AR', 'CO')
ASIA = ('ID', 'KR', 'IL', 'NP', 'PH', 'PK', 'TR', 'VN', 'IS', 'AM', 'UZ', 'RU')
AFRICA = ('NG', 'TZ', 'ZA')
INT_MAX = sys.maxsize

CONTINENT_MAPPING = {
    "america": AMERICA,
    "europe": EUROPE,
    "oceania": OCEANIA,
    "latin": LATIN,
    "asia": ASIA,
    "africa": AFRICA
}

PREFIX_OVERRIDES = {
    Genre.rnb: 'rb',
    Gender.mixed: 'mx'
}

CLOSE_POPULARITY_RANGE = 50
CLOSE_DEBUT_RANGE = 5

PRINT_COLOR_MAPPING = {
    "type": {
        Members.solo: 'green',
        Members.group: 'red',
    },
    "genre": {
        Genre.pop: 'blue',
        Genre.indie: 'cyan',
        Genre.hiphop: 'yellow',
        Genre.rock: 'magenta',
        Genre.rnb: 'bright_blue',
    },
    "gender": {
        Gender.male: 'blue',
        Gender.female: 'magenta',
        Gender.mixed: 'white',
    },
    "score": {
        '2': 'green',
        '2-3': 'orange',
        '3': 'yellow',
        '5': 'red'
    }
}

hint_alt_const = ('**:mag_right: You should try using a hint** to get more information - if you can\'t use a hint, then ')