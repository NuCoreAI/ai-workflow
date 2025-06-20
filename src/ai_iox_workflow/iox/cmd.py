from dataclasses import dataclass, field
from .editor import Editor


@dataclass
class CommandParameter:
    """
    Definition of a parameter for a command.
    """

    id: str
    editor: Editor
    name: str | None = None
    init: str | None = None
    optional: bool | None = None


@dataclass
class Command:
    """
    Defines the structure of commands that a node can send or accept.
    """

    id: str
    name: str | None = None
    format: str | None = None
    parameters: list[CommandParameter] = field(default_factory=list)
