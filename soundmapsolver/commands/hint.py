from ..const import hint_alt_const
from ..command import Command
from ..artist import Artist


def callback(command: Command):
    command.solver._copy_to_clipboard(
        f'{hint_alt_const}\n\n-# If you can\'t see the button, you need to update your game in the App Store.'
    )


command = Command(
    name='hint',
    description='',
    usage='',
    callback=callback
)

__all__ = ['command']
