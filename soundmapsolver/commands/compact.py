from ..command import Command
from ..artist import Artist


def callback(command: Command):
    command.solver.compact_mode = not command.solver.compact_mode
    command.solver.print_error('Compact mode has been disabled.') if not command.solver.compact_mode else command.solver.print_success('Compact mode has been enabled.')

command = Command(
    name='compact',
    description='Shows the table of artists in a compact format by abbreviating information.',
    usage='compact',
    callback=callback
)

__all__ = ['command']
