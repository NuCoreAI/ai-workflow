import textwrap
from dataclasses import dataclass, field
from .editor import Editor
from .cmd import Command


@dataclass
class NodeProperty:
    """
    Defines attributes and properties of a node.
    """

    id: str
    editor: Editor
    name: str = None
    hide: bool = None

    def __str__(self):
        return f"{self.name}: {self.editor}"


@dataclass
class NodeCommands:
    """
    Specifies the commands that a node can send and accept.
    """

    sends: list[Command] = field(default_factory=list)
    accepts: list[Command] = field(default_factory=list)


@dataclass
class NodeLinks:
    """
    Defines control and response link references for a node.
    """

    ctl: list[str] = field(default_factory=list)
    rsp: list[str] = field(default_factory=list)


@dataclass
class NodeDef:
    """
    Describes the properties, commands, and links of a node, defining its
    behavior and capabilities within the system.
    """

    id: str
    properties: list[NodeProperty]
    cmds: NodeCommands
    nls: str = None
    icon: str = None
    links: NodeLinks = None

    def __str__(self):
        s = [f"Node type: {self.id} ({self.nls})"]

        s.append(textwrap.indent("Properties:", "  "))
        for prop in self.properties:
            s.append(textwrap.indent(str(prop), "  - "))

        return "\n".join(s)
