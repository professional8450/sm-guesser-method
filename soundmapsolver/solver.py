import csv
import pyperclip
import soundmapsolver
from enum import Enum
from collections import Counter, defaultdict
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from typing import Optional, List, Tuple, Dict, Counter
from .artist import Artist
from .command import Command
from .commands import commands
from .const import *
from .history import History
from .rules import Rule, ExactRule, ExclusionRule, WithinRule, InRule


class Solver(object):
    def __init__(self):
        self.artists: Optional[List[Artist]] = None
        self.message_formats: Dict[str, str] = {}
        self.commands: Dict[str, Command] = commands
        self.warnings: Dict[str, str] = {}
        self.history: List[History] = []
        self.nick_jonas: Artist = None
        self.russ: Artist = None
        self.compact_mode: bool = False

        for command in self.commands.values():
            command.init(self)

        self.console = Console()

    def import_csv_file(self, *, path: str):
        try:
            with open(path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                self.artists = [Artist(**row) for row in csv_reader]
                self.artists = sorted(self.artists, key=lambda artist: artist.popularity, reverse=False)
        except OSError:
            self.print_error(f'Could not import artists. Commands will not work. ({path})')

    def print(self, *, content: str, text_color: str = "white", background_color: Optional[str] = None):
        self.console.print(f'[{text_color}{f" on {background_color}" if background_color else ""}]{content}[/]')

    def print_error(self, content: str):
        self.print(content=f'{content}', text_color="red")

    def print_warning(self, content: str):
        self.print(content=f'{content}', text_color="yellow")

    def run(self):
        if not self.artists:
            self.print_error('Artists have not been loaded. The solver could not be run.')
            return

        print(f'The Method v{soundmapsolver.__version__}, Python {sys.version}')

        while True:
            command = input('>> ')
            command, arguments = self._parse_command(command)
            if command:
                command.run(arguments)

    def _parse_command(self, command: str) -> Tuple[Optional[Command], List[str]]:
        spl = command.split(" ")
        command = self.commands.get(spl[0].lower())

        if not command:
            return self.commands.get('query'), spl

        return command, spl[1:]

    def _format_value(self, *, value: str, color: str, compact: bool = False):
        return f'[{color}]{value.replace(' or ', '-')}[/]' if not compact else f'[{color}]{value[0] if value != 'R&B' else 'RB'}[/]'

    def _infer_first_guess(self, *, query: str) -> Optional[Artist]:
        rules = self._build_rules(query)
        genre_rules = [rule for rule in rules if rule.attribute == 'genre']
        popularity_rules = [rule for rule in rules if rule.attribute == 'popularity']

        debut_rules = [rule for rule in rules if rule.attribute == 'debut']
        gender_rules = [rule for rule in rules if rule.attribute == 'gender']

        if len(genre_rules) != 1 or len(popularity_rules) != 1 or len(debut_rules) > 1 or len(gender_rules) > 1:
            return

        genre = genre_rules[0]._original_value
        popularity = popularity_rules[0]._original_value
        artist = [artist for artist in self.artists if artist.genre == genre and artist.popularity == popularity]
        if len(artist) > 1:
            return

        return artist[0]

    def _get_path_string_size(self, size):
        lower = int(size)
        upper = lower + 1

        if size == lower:
            return str(lower)
        return f"{lower} or {upper}"

    def _get_path_size(self, *, start: Artist, end: Artist):
        path = self._calculate_path(start=start, end=end)
        if isinstance(path[-1][0], list):
            return len(path) + 0.5
        return len(path)

    def entropy(self, *, query: str, options: List[Artist]) -> Artist:
        if not options or len(options) == 0:
            return []

        if len(options) < 3:
            return options[0]

        if len(options) == 3:
            return options[1]

        best_artist = None
        best_max_group_size = float('inf')

        for artist in options:
            partitions = defaultdict(list)

            for answer in options:
                if artist == answer:
                    continue

                calculation_query = f'{query} {self._build_query(start=artist, end=answer)}'
                rules = self._build_rules(calculation_query)
                remaining = self._get_passing_artists(rules=rules, artists=options)

                if remaining:
                    key = frozenset(a.name for a in remaining)
                    partitions[key].append(answer)

            if partitions:
                max_group_size = max(len(group) for group in partitions.values())

                if max_group_size < best_max_group_size:
                    best_max_group_size = max_group_size
                    best_artist = artist

        return best_artist or options[0]

    def _first_guess_calculation(
            self,
            *,
            artists: List[Artist],
            query: Optional[str] = None
    ):
        self.print(content="Calculating best first guess, as only one rule was provided.", text_color='white', background_color='red')

        guess = None

        if query == 'p':
            guess = self._search('Nick Jonas')[0]
        if query == 'r' or query == 'g':
            guess = self._search('Thirty Seconds to Mars')[0]
        if query == 'rb':
            guess = self._search('Omarion')[0]
        if query == 'i':
            guess = self._search('Faye Webster')[0]
        if query == 'h':
            guess = self._search('Russ')[0]
        if query == 'm' or query == 'us' or query == 'US':
            guess = self._search('Kevin Gates')[0]
        if query == 's':
            guess = self._search('2 Chainz')[0]
        if query == 'gb' or query == 'GB':
            guess = self._search('Rita Ora')[0]
        if query == 'f':
            guess = self._search('Alessia Cara')[0]
        if query == 'mx':
            guess = self._search('No Doubt')[0]
        if not guess:
            guess = self.entropy(query=query, options=artists)

        if guess:
            self.print(content=f"{guess.name} is the best starting guess!", text_color='green', background_color='black')

        return guess

    def _print_artists(
            self,
            *,
            artists: List[Artist],
            title: str = "Artists",
            query: Optional[str] = None,
            copy: bool = True,
            inferred_first_guess: Optional[Artist] = None,
            rules: Optional[List[Rule]] = None
    ):
        recommend_guess = None

        if self.compact_mode:
            return self._print_compact(artists=artists, title=title, query=query, copy=copy, inferred_first_guess=inferred_first_guess, rules=rules)
        if rules and len(rules) == 1:
            recommend_guess = self._first_guess_calculation(artists=artists, query=query)

        table = Table(title=f'[b]{title}[/]', title_justify="left", title_style='none')
        table.add_column("Name", justify="left")
        table.add_column("Debut", justify="center")
        table.add_column("Popularity", justify="center")
        table.add_column("Type", justify="left")
        table.add_column("Genre", justify="left")
        table.add_column("Country", justify="left")
        table.add_column("Gender", justify="left")

        if not recommend_guess:
            if len(artists) > 2:
                recommend_guess = self._recommended_guess_algorithm(artists)
            else:
                recommend_guess = None

        for artist in artists:
            table.add_row(
                f'[b][yellow]{artist.name}[/yellow][/b]' if artist == recommend_guess else artist.name,
                f'[b][yellow]{artist.debut}[/yellow][/b]' if artist == recommend_guess else str(artist.debut),
                f'[b][yellow]{artist.popularity}[/yellow][/b]' if artist == recommend_guess else str(artist.popularity),
                self._format_value(value=artist.type.value, color=PRINT_COLOR_MAPPING['type'][artist.type]),
                self._format_value(value=artist.genre.value, color=PRINT_COLOR_MAPPING['genre'][artist.genre]),
                artist.country.upper(),
                self._format_value(value=artist.gender.value, color=PRINT_COLOR_MAPPING['gender'][artist.gender]),
            )

        panels = []

        if query:
            flags, warnings = self._build_warnings(query)
        else:
            flags = []
            warnings = []

        inferred_first_guess = inferred_first_guess
        if rules and not inferred_first_guess:
            infer_query = query.split(' ; ')
            if len(infer_query) >= 2:
                infer_query = infer_query[0]
            else:
                infer_query = query

            inferred_first_guess = self._infer_first_guess(query=infer_query)

        # if inferred_first_guess:
        #     panel = Panel(Align.center(inferred_first_guess.name), title="Inferred first guess", expand=False)
        #     panels.append(panel)
        #     if inferred_first_guess.ranks[0] > 200:
        #         if not ("+" in query):
        #             warnings = [warning for warning in warnings if not warning[13:].startswith('I recommend using a better first guess')]
        #             warnings.append(
        #                 f"-# :warning: {inferred_first_guess.name} is not a good guess to start with. I recommend using Nick Jonas as your starting guess in the future "
        #                 f"to improve your chances of getting 2 or even 3 gems.\n-# (Your guess ranked {self._ordinal(inferred_first_guess.ranks[0])} out of 1000 artists.)"
        #             )
        #             flags.append('(inferred)')
        #             warnings = list(reversed(warnings))

        if len(flags) >= 1:
            panel = Panel(f", ".join(flags), title="Enabled flags", expand=False)
            panels.append(panel)

        if len(artists) >= 1 and len(artists) < 1000:
            self.console.print(table)
        if len(artists) == 1000:
            return self.print_warning('Your query is too broad.')
        if len(artists) == 0:
            return self.print_warning('No artists exist that match your query.')
        if len(artists) > 2:
            #recommend_guess = self._recommended_guess_algorithm(artists)

            odds = (1 / len(artists)) * 100
            odds = f'{odds:.1f}%'
            panel = Panel(
                f"[b]{recommend_guess.name}[/] - 1 in {len(artists)} ({odds})",
                title="Recommended guess",
                expand=False
            )
            panels.append(panel)

        if len(artists) == 1:
        #    if copy:
        #        if inferred_first_guess:
        #            path_a = self._get_path_size(start=inferred_first_guess, end=artists[0])
        #            path_b = self._get_path_size(start=self.nick_jonas, end=artists[0])
        #
        #            if path_a > path_b:
        #                warnings.append(f"If you had started with **Nick Jonas**, it could have been solved in {self._get_path_string_size(path_b)} guesses.")
                self._copy_answer(artist=artists[0], warnings=warnings)

        if len(artists) > 1 and 'hint' in query:
            if copy:
                self._copy_suggest_hint(
                    artist=recommend_guess or artists[0], odds=(1 / len(artists) * 100), amount=len(artists)
                )

                self._add_to_history(artist=recommend_guess, query=query.replace('hint', ''), inferred_first_guess=inferred_first_guess)
        else:
            if len(artists) == 2:
                if copy:
                    self._copy_coin_flip(artist_a=artists[0], artist_b=artists[1], warnings=warnings)
            if len(artists) > 2:
                if copy:
                    if len(rules) > 1:
                        self._copy_with_odds(artist=recommend_guess, odds=(1 / len(artists) * 100), amount=len(artists),
                                             warnings=warnings)
                    else:
                        self._copy_first_guess(artist=recommend_guess)

                self._add_to_history(artist=recommend_guess, query=query, inferred_first_guess=inferred_first_guess)

        self.console.print(Columns(reversed(panels)))
        #self.print_warning(f'Average amount of guesses for {self.russ.name}: {sum([artist.alt for artist in artists]) / len(artists)}')
        #self.print_warning(f'Average amount of guesses for {self.nick_jonas.name}: {sum([artist.score for artist in artists]) / len(artists)}')

    def _copy_suggest_hint(self, *, artist, odds, amount):
        odds = f'{odds:.1f}%'

        message = f'If you do not want/can\'t use a hint, then **{self.message_formats.get('odds').replace("{ANSWER}", artist.name).replace("{AMOUNT}",
                                                                                            str(amount)).replace("{ODDS}", odds)}.**'
        return self._copy_to_clipboard(f'{hint_const}\n\n{message}\n-# If you can\'t see the button, you need to update your game in the App Store.')

    def set_answer_message(self, format: str):
        self.message_formats['answer'] = format

    def add_warning_message(self, *, flag: str, message: str):
        self.warnings[flag] = message

    def set_coin_flip_message(self, format: str):
        self.message_formats['coin_flip'] = format

    def set_odds_message(self, format: str):
        self.message_formats['odds'] = format

    def _copy_with_odds(self, *, artist: Artist, amount: int, odds: float, warnings: List[str] = None):
        odds = f'{odds:.1f}%'

        message = self.message_formats.get('odds').replace("{ANSWER}", artist.name).replace("{AMOUNT}",
                                                                                            str(amount)).replace(
            "{ODDS}", odds)
        return self._copy_with_warnings(message, warnings=warnings)

    def _copy_first_guess(self, *, artist: Artist):
        return self._copy_to_clipboard(f'I recommend using `{artist.name}` as your first guess today!')

    def _add_to_history(self, *, artist: Artist, query: str, inferred_first_guess: Optional[Artist] = None):
        history = History(recommended_guess=artist, query=query, inferred_first_guess=inferred_first_guess)
        self.history.append(history)

    def _get_from_history(self, search: str):
        self.history = sorted(self.history, key=lambda item: item.timestamp, reverse=True)
        for item in self.history:
            if item.recommended_guess.name.lower().startswith(search.lower()):
                return item
        return None

    def _build_warnings(self, query: str):
        if "+" in query and "~" not in query:
            return [], []

        result = []
        flags = []
        for word in query.split():
            if word.startswith("-"):
                flag = word[1:]
                flags.append(word)
                warning = self.warnings.get(flag)
                if warning:
                    result.append(f'-# :triangular_flag_on_post: {warning}')
        return flags, result

    def _copy_to_clipboard(self, content: str):
        pyperclip.copy(content)

    def _copy_answer(self, *, artist: Artist, warnings: List[str] = None):
        n = [warning for warning in warnings if warning[13:].startswith('I recommend using a better first guess')]
        if n and artist.score <= 3.5:
            format = "It's most likely `{ANSWER}`! \N{PARTY POPPER}\n\nIt would have taken **{SCORE}** guesses with **Nick Jonas.**"
        else:
            format = self.message_formats.get('answer')

        message = (format.replace("{ANSWER}", artist.name).replace("{SCORE}", self._get_path_string_size(artist.score)))
        return self._copy_with_warnings(message, warnings=warnings)

    def _copy_coin_flip(self, *, artist_a: Artist, artist_b: Artist, warnings: List[str] = None):
        message = (self.message_formats.get('coin_flip').replace("{ANSWER}", artist_a.name, 1).replace("{ANSWER}", artist_b.name, 1))
        return self._copy_with_warnings(message, warnings=warnings)

    def _copy_with_warnings(self, content: str, *, warnings: List[str] = None):
        if warnings:
            content += "\n\n"
            content += "\n".join(warnings)

        pyperclip.copy(content)

    def _symbol(self, condition, true_symbol, false_symbol=""):
        return true_symbol if condition else false_symbol

    def _build_query(self, *, start: Artist, end: Artist) -> str:
        query = (
            f"{start.debut}"
            f"{self._symbol(start.debut > end.debut, 'v')}"
            f"{self._symbol(start.debut < end.debut, '^')}"
            f"{self._symbol(0 < abs(start.debut - end.debut) <= 5, 'y')} "
            f"{start.popularity}"
            f"{self._symbol(start.popularity < end.popularity, 'v')}"
            f"{self._symbol(start.popularity > end.popularity, '^')}"
            f"{self._symbol(abs(start.popularity - end.popularity) <= 50, 'y')} "
            f"{self._symbol(start.type != end.type, '!')}{start.type.value[0].lower()} "
            f"{self._symbol(start.genre != end.genre, '!')}"
            f"{'rb' if start.genre == Genre.rnb else start.genre.value[0].lower()} "
            f"{self._symbol(start.gender != end.gender, '!')}"
            f"{'mx' if start.gender == Gender.mixed else start.gender.value[0].lower()} "
            f"{self._symbol(start.country == end.country, "", self._symbol(self._get_continent(start.country) == self._get_continent(end.country), "", "!"))}"
            f"{start.country}"
            f"{self._symbol(self._get_continent(start.country) == self._get_continent(end.country) and start.country != end.country, "y", "")}"
        )

        return query

    def _recommended_guess_algorithm(self, options: List[Artist]) -> Artist:
        if len(options) > 5:
            pivot_index = len(options) // 2
            pivot = options[pivot_index]
            above = options[pivot_index + 1]
            below = options[pivot_index - 1]

            average = sum(artist.debut for artist in options) / len(options)

            candidates = [pivot, above, below]
            closest_artist = min(candidates, key=lambda artist: abs(artist.debut - average))

            return closest_artist
        else:
            return options[len(options) // 2]

    def _calculate_path(self, *, start: Artist, end: Artist):
        init_end = end
        answer = None
        query = ""

        history = [(start, None), ]
        while (not answer) or len(answer) > 2:
            query = f'{query} {self._build_query(start=start, end=end)}'
            rules = self._build_rules(query)
            answer = self._get_passing_artists(rules=rules)

            recommended_guess = self._recommended_guess_algorithm(answer)
            history[-1] = (history[-1][0], len(answer))

            if len(answer) > 2:
                history.append((recommended_guess, None))
                if init_end == recommended_guess:
                    break
                start = recommended_guess
            else:
                if len(answer) == 1:
                    history.append((recommended_guess, None))
                if len(answer) == 2:
                    history.append(([answer[0], answer[1]], None))

        return history

    def _build_rules(self, query: str):
        command_parts = query.split()
        rules: [Rule] = []

        for part in command_parts:
            yellow_split = part.split('y') if 'y' in part else part.split('Y')
            yellow = True if len(yellow_split) == 2 else False
            part = yellow_split[0] if len(yellow_split) == 2 else part

            exclusion_split = part.split('!')
            exclusion = True if len(exclusion_split) == 2 else False
            part = exclusion_split[1] if len(exclusion_split) == 2 else part

            direction = None

            if part.endswith('v') or part.endswith('V'):
                direction = 'down'
                part = part[:-1]
            if part.endswith('^'):
                direction = 'up'
                part = part[:-1]

            if part.isdigit() and len(part) == 4:
                part = int(part)
                rule = None

                if direction is None:
                    if exclusion:
                        rule = ExclusionRule(attribute='debut', values=[part])
                    else:
                        rule = ExactRule(attribute='debut', value=part)

                elif direction == 'down':
                    if yellow:
                        rule = WithinRule(attribute='debut', min=part - (CLOSE_DEBUT_RANGE + 1), max=part)
                    else:
                        rule = WithinRule(attribute='debut', min=-INT_MAX, max=part - CLOSE_DEBUT_RANGE)

                elif direction == 'up':
                    if yellow:
                        rule = WithinRule(attribute='debut', min=part, max=part + CLOSE_DEBUT_RANGE + 1)
                    else:
                        rule = WithinRule(attribute='debut', min=part + CLOSE_DEBUT_RANGE, max=INT_MAX)

                rules.append(rule)
                continue

            if part.isdigit() and len(part) <= 3:
                if direction is None:
                    if not exclusion:
                        rule = ExactRule(attribute='popularity', value=int(part))
                    else:
                        rule = ExclusionRule(attribute='popularity', values=[int(part)])
                else:
                    if direction != 'down':
                        if yellow:
                            rule = WithinRule(attribute='popularity', min=int(part) - (CLOSE_POPULARITY_RANGE + 1),
                                              max=int(part))
                        else:
                            rule = WithinRule(attribute='popularity', min=-INT_MAX,
                                              max=int(part) - CLOSE_POPULARITY_RANGE)
                    else:
                        if yellow:
                            rule = WithinRule(attribute='popularity', min=int(part),
                                              max=int(part) + CLOSE_POPULARITY_RANGE + 1)
                        else:
                            rule = WithinRule(attribute='popularity', min=int(part) + CLOSE_POPULARITY_RANGE,
                                              max=INT_MAX)

                rule._original_value = int(part)
                rules.append(rule)
                continue

            if part in ('s', 'g'):
                if not exclusion:
                    rule = ExactRule(attribute='members',
                                     value=self._enum_from_first_letter(prefix=part.lower(), enum_class=Members))
                else:
                    rule = ExclusionRule(attribute='members',
                                         values=[self._enum_from_first_letter(prefix=part.lower(), enum_class=Members)])
                rules.append(rule)

            if part in ('h', 'p', 'r', 'rb', 'i'):
                if not exclusion:
                    rule = ExactRule(attribute='genre',
                                     value=self._enum_from_first_letter(prefix=part.lower(), enum_class=Genre))
                else:
                    rule = ExclusionRule(attribute='genre',
                                         values=[self._enum_from_first_letter(prefix=part.lower(), enum_class=Genre)])

                rule._original_value = self._enum_from_first_letter(prefix=part.lower(), enum_class=Genre)
                rules.append(rule)
                continue

            if len(part) == 2 and part not in ('h', 'p', 'r', 'rb', 'i', 'mx') and not part.isdigit():
                if self._get_continent(part.upper()) == 'unknown':
                    break

                if (not exclusion) and (not yellow):
                    rule = ExactRule(attribute='country', value=part.upper())
                else:
                    if yellow:
                        rule = InRule(attribute='country', values=CONTINENT_MAPPING[self._get_continent(part.upper())])
                        rules.append(ExclusionRule(attribute='country', values=[part.upper()]))
                    else:
                        rule = ExclusionRule(attribute='country',
                                             values=CONTINENT_MAPPING[self._get_continent(part.upper())])

                rules.append(rule)
                continue

            if part in ('m', 'f', 'mx'):
                if not exclusion:
                    rule = ExactRule(attribute='gender',
                                     value=self._enum_from_first_letter(prefix=part.lower(), enum_class=Gender))
                else:
                    rule = ExclusionRule(attribute='gender',
                                         values=[self._enum_from_first_letter(prefix=part.lower(), enum_class=Gender)])
                rules.append(rule)

            if part in ('america', 'europe', 'latin', 'oceania', 'asia', 'africa'):
                if exclusion:
                    rule = ExclusionRule(attribute='country', values=CONTINENT_MAPPING[part])
                else:
                    rule = InRule(attribute='country', values=CONTINENT_MAPPING[part])
                rules.append(rule)
                continue

        return rules

    def _get_passing_artists(self, *, rules: List[Rule], artists: Optional[List[Artist]] = None):
        if not artists:
            artists = self.artists

        return [artist for artist in artists if all(rule(artist) for rule in rules)]

    def _calculate_odds(self, *, artist: Artist):
        result = {
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0
        }
        paths = []

        for answer in self.artists:
            if answer == artist:
                continue

            paths.append(self._calculate_path(start=artist, end=answer))

        counter: Counter[str] = Counter()
        for path in paths:
            if isinstance(path[-1][0], list):
                counter[f'{len(path)} or {len(path) + 1}'] += 1
            else:
                counter[f'{len(path)}'] += 1

        total = len(self.artists) - 1
        probability_of_2 = counter['2'] + counter['2 or 3'] / 2
        probability_of_2_3 = probability_of_2 + counter['3'] + counter['2 or 3'] / 2 + counter['3 or 4'] / 2
        probability_of_2_4 = probability_of_2_3 + counter['4'] + counter['3 or 4'] / 2 + counter['4 or 5'] / 2

        return {
            2: probability_of_2 / total * 100,
            3: probability_of_2_3 / total * 100,
            4: probability_of_2_4 / total * 100,
            5: 100 - (probability_of_2_4 / total) * 100
        }

    def _enum_from_first_letter(self, *, enum_class: type[Enum], prefix: str):
        for member in enum_class:
            custom_prefix = PREFIX_OVERRIDES.get(member)

            if custom_prefix:
                if custom_prefix == prefix:
                    return member

            elif member.value.lower().startswith(prefix.lower()):
                return member

    def _ordinal(self, n):
        if 11 <= n % 100 <= 13:
            suffix = "th"
        else:
            suffix = {
                1: "st",
                2: "nd",
                3: "rd"
            }.get(n % 10, "th")
        return f"{n}{suffix}"

    def _print_odds_panel(self, *, artist: Artist):
        return self.print(content="The odds panel has been disabled.", text_color='white', background_color='red')

        odds = self._calculate_odds(artist=artist)
        odds = {key: f"{value:.1f}%" for key, value in odds.items()}
        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))

        table.add_column("Guesses", justify="left")
        table.add_column("Odds", justify="left")

        if artist.ranks:
            table.add_row("2", f'{odds.get(2)} ({self._ordinal(artist.ranks[0])})')
            table.add_row("within 3", f'{odds.get(3)} ({self._ordinal(artist.ranks[1])})')
            table.add_row("within 4", f'{odds.get(4)} ({self._ordinal(artist.ranks[2])})')
            table.add_row("5+", f'{odds.get(5)} ({self._ordinal(artist.ranks[3])})')
        else:

            table.add_row("2", f'{odds.get(2)}')
            table.add_row("within 3", f'{odds.get(3)}')
            table.add_row("within 4", f'{odds.get(4)}')
            table.add_row("5+", f'{odds.get(5)}')

        panel = Panel(table, title="First guess statistics", expand=False)
        self.console.print(panel)

    def _search(self, search: str):
        result = []

        for artist in self.artists:
            if artist.name.lower().startswith(search.lower()):
                result.append(artist)

        for artist in result:
            if artist.name.lower() == search.lower():
                return [artist]

        return result

    def _get_continent(self, param: str):
        country = param.upper()
        if country in AMERICA:
            return 'america'
        if country in EUROPE:
            return 'europe'
        if country in OCEANIA:
            return 'oceania'
        if country in LATIN:
            return 'latin'
        if country in ASIA:
            return 'asia'
        if country in AFRICA:
            return 'africa'
        return 'unknown'

    def _print_compact(
            self,
            *,
            artists: List[Artist],
            title: str = "Artists",
            query: Optional[str] = None,
            copy: bool = True,
            inferred_first_guess: Optional[Artist] = None,
            rules: Optional[List[Rule]] = None
    ):

        table = Table(title=f'[b]{title}[/]', title_justify="left", title_style='none')
        table.add_column("Name", justify="left")
        table.add_column("Information", justify="left")

        if len(artists) > 2:
            recommend_guess = self._recommended_guess_algorithm(artists)
        else:
            recommend_guess = None

        for artist in artists:
            information_string = ', '.join(
                [
                    str(artist.debut),
                    str(artist.popularity),
                    self._format_value(value=artist.type.value, color=PRINT_COLOR_MAPPING['type'][artist.type], compact=True),
                    self._format_value(value=artist.genre.value, color=PRINT_COLOR_MAPPING['genre'][artist.genre], compact=True),
                    artist.country.upper(),
                    self._format_value(value=artist.gender.value, color=PRINT_COLOR_MAPPING['gender'][artist.gender], compact=True),
                    #self._format_value(value=str(self._get_path_string_size(artist.score)), color=PRINT_COLOR_MAPPING['score'].get(str(artist.score), 'white'), compact=False)
                ]
            )

            table.add_row(
                f'[b][yellow]{artist.name}[/yellow][/b]' if artist == recommend_guess else artist.name,
                information_string
            )

        panels = []

        if query:
            flags, warnings = self._build_warnings(query)
        else:
            flags = []
            warnings = []

        inferred_first_guess = inferred_first_guess
        if rules and not inferred_first_guess:
            infer_query = query.split(' ; ')
            if len(infer_query) >= 2:
                infer_query = infer_query[0]
            else:
                infer_query = query

            inferred_first_guess = self._infer_first_guess(query=infer_query)

        # if inferred_first_guess:
        #     panel = Panel(Align.center(inferred_first_guess.name), title="Inferred first guess", expand=False)
        #     panels.append(panel)
        #     if inferred_first_guess.ranks[0] > 200:
        #         if not ("+" in query):
        #             warnings = [warning for warning in warnings if not warning[13:].startswith('I recommend using a better first guess')]
        #             warnings.append(
        #                 f"-# :warning: {inferred_first_guess.name} is not a good guess to start with. I recommend using Nick Jonas as your starting guess in the future "
        #                 f"to improve your chances of getting 2 or even 3 gems.\n-# (Your guess ranked {self._ordinal(inferred_first_guess.ranks[0])} out of 1000 artists.)"
        #             )
        #             flags.append('(inferred)')
        #             warnings = list(reversed(warnings))

        if len(flags) >= 1:
            panel = Panel(f", ".join(flags), title="Enabled flags", expand=False)
            panels.append(panel)

        if len(artists) >= 1 and len(artists) < 1000:
            self.console.print(table)
        if len(artists) == 1000:
            return self.print_warning('Your query is too broad.')
        if len(artists) == 0:
            return self.print_warning('No artists exist that match your query.')
        if len(artists) > 2:
            recommend_guess = self._recommended_guess_algorithm(artists)

            odds = (1 / len(artists)) * 100
            odds = f'{odds:.1f}%'
            panel = Panel(
                f"[b]{recommend_guess.name}[/] - 1 in {len(artists)} ({odds})",
                title="Recommended guess",
                expand=False
            )
            panels.append(panel)

        if len(artists) == 1:
        #    if copy:
        #        if inferred_first_guess:
        #            path_a = self._get_path_size(start=inferred_first_guess, end=artists[0])
        #            path_b = self._get_path_size(start=self.nick_jonas, end=artists[0])
        #
        #            if path_a > path_b:
        #                warnings.append(f"If you had started with **Nick Jonas**, it could have been solved in {self._get_path_string_size(path_b)} guesses.")
                self._copy_answer(artist=artists[0], warnings=warnings)

        if len(artists) == 2:
            if copy:
                self._copy_coin_flip(artist_a=artists[0], artist_b=artists[1], warnings=warnings)
        if len(artists) > 2:
            recommend_guess = self._recommended_guess_algorithm(artists)
            if copy:


                self._copy_with_odds(artist=recommend_guess, odds=(1 / len(artists) * 100), amount=len(artists),
                                     warnings=warnings)
            self._add_to_history(artist=recommend_guess, query=query, inferred_first_guess=inferred_first_guess)

        self.console.print(Columns(reversed(panels)))