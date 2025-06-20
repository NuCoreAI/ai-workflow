from textwrap import indent
from dataclasses import dataclass, field
from .nodedef import NodeDef


@dataclass
class TypeInfo:
    id: str
    val: str


@dataclass
class Property:
    id: str
    value: str
    formatted: str
    uom: str
    prec: int = field(default=None)
    name: str = field(default=None)


@dataclass
class Node:
    flag: int
    nodeDefId: str
    address: str
    name: str
    family: int
    hint: str
    type: str
    enabled: bool
    deviceClass: int
    wattage: int
    dcPeriod: int
    startDelay: int
    endDelay: int
    pnode: str
    node_def: NodeDef = None
    rpnode: str = field(default=None)
    sgid: int = field(default=None)
    typeInfo: list[TypeInfo] = field(default_factory=list)
    property: list[Property] = field(default_factory=list)
    parent: str = field(default=None)
    custom: dict = field(default=None)
    devtype: dict = field(default=None)

    def __str__(self):
        return "\n".join(
            (
                f"Node: {self.name} [{self.address}]",
                indent(str(self.node_def), "  "),
            )
        )
