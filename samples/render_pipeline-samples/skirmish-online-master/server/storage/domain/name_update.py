from dataclasses import dataclass


@dataclass
class NameUpdate:
    id: int
    name: str
