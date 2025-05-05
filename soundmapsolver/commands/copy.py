from ..command import Command
from ..artist import Artist


def callback(command: Command, search: str):
    query = command.solver._get_from_history(search)

    if query:
        copy = " ".join(word for word in query.query.split() if not word.startswith("-"))
        command.solver._copy_to_clipboard(f'{copy} ')
        command.solver.print(
            content=f'Copied [{query.recommended_guess.name}] = [b]{copy}[/b] to clipboard.',
            text_color='green'
        )

    else:
        command.solver.print_error('I could not find that.')


command = Command(
    name='copy',
    description='Copies a query based on the recommended guess.',
    usage='copy <recommended guess>',
    callback=callback,
    alias=['c']

)

__all__ = ['command']