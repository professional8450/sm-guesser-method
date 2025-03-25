import importlib
import pkgutil

# Dictionary to store loaded commands
commands = {}

# Discover all modules in the "commands" package
for _, module_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f".{module_name}", package=__name__)

    if hasattr(module, "command"):  # Ensure `command` exists
        commands[module.command.name] = module.command  # Store by name
        if module.command.aliases:
            for alias in module.command.aliases:
                commands[alias] = module.command

__all__ = ["commands"]  # Only export `commands`
