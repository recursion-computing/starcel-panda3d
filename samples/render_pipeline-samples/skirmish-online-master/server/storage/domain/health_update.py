from dataclasses import dataclass


@dataclass
class HealthUpdate:
    id: int
    health: int
