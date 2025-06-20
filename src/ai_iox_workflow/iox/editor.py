from dataclasses import dataclass, field
from .uom import UOMEntry, supported_uoms


@dataclass
class EditorSubsetRange:
    """
    Defines a discrete set of allowed values for an editor range,
    using spans (e.g., '0-5') and individual values (e.g., '7,9').
    """

    uom: UOMEntry = field(metadata={"choices": supported_uoms})
    subset: str
    names: dict = field(default_factory=dict)

    def __str__(self):
        parts = []
        for s in self.subset.split(","):
            s = s.strip()
            if "-" in s:
                # It's a range 'a-b'
                parts.append(s)
                parts.append(
                    ", ".join([f"{k} => {v}" for k, v in self.names.items()])
                )
            else:
                # Single value
                val_name = self.names.get(s)
                if val_name:
                    parts.append(f"{s} => {val_name}")
                else:
                    parts.append(s)
        subset_str = ", ".join(parts)
        return f"Discrete values: {subset_str} {self.uom}"


@dataclass
class EditorMinMaxRange:
    """
    Defines a continuous range with min, max, precision, and step attributes.
    """

    uom: UOMEntry = field(metadata={"choices": supported_uoms})
    min: float
    max: float
    prec: float = None
    step: float = None
    names: dict = field(default_factory=dict)

    def __str__(self):
        if self.uom.id == "25":
            label = "Discrete values"
        else:
            label = "Range"

        parts = [f"{label}: {self.min} -> {self.max} {self.uom}"]

        if self.step:
            parts.append(f" by step of {self.step}.")

        if self.names:
            parts.append(" mapping: ")
            parts.append(
                ", ".join([f"{k} => {v}" for k, v in self.names.items()])
            )
        return "".join(parts)


@dataclass
class Editor:
    """
    Definition of an editor, used to render a value or allow selection.
    It defines allowed values through one or more ranges.
    """

    id: str
    ranges: list[EditorSubsetRange | EditorMinMaxRange]

    def __str__(self):
        return "; ".join([f"{r}" for r in self.ranges])
