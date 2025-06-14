import sys
from .enums import Members, Genre, Gender

AMERICA = ('US', 'CA', 'MX', 'BB', 'PR', 'HT', 'JM')
EUROPE = ('FR', 'DE', 'GB', 'NO', 'BE', 'DK', 'ES', 'IE', 'IT', 'NL', 'RO', 'SE', 'UA', 'HR', 'IS')
OCEANIA = ('AU', 'NZ')
LATIN = ('BR', 'AR', 'CO', 'CL', 'UY', 'VE')
ASIA = ('ID', 'KR', 'NP', 'PH', 'PK', 'TR', 'VN', 'AM', 'RU', 'JP', 'KG')
AFRICA = ('NG', 'TZ', 'ZA', 'GH', 'CD', 'DZ')

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
    Gender.mixed: 'mx',
    Genre.kpop: 'k'
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
        Genre.kpop: 'orange'
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

hint_alt_const = ('Use a hint, or (if you can\'t use a hint): ')