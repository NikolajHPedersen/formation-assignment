# TODO: make a debug mode that uses a mock data file instead of the real data file
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def normalize_role(role: str) -> str:
    return role.strip().upper()


def normalize_foot(foot: str) -> str:
    normalized_foot = foot.strip().lower()
    if normalized_foot not in {"left", "right"}:
        raise ValueError(f"Invalid foot value: {foot!r}")
    return normalized_foot


@dataclass(frozen=True)
class FormationSlot:
    slot_id: str
    role: str

    def __init__(self, slot_id: str, role: str) -> None:
        object.__setattr__(self, "slot_id", slot_id.upper())
        object.__setattr__(self, "role", normalize_role(role))


@dataclass(frozen=True)
class AssignmentBreakdown:
    preference: int
    attributes: int
    footedness: int
    total: int


@dataclass(frozen=True)
class Player:
    name: str
    preferred_positions: tuple[str, ...]
    attributes: Mapping[str, int]
    foot: str

    def __init__(
        self,
        name: str,
        preferred_positions: tuple[str, ...],
        attributes: Mapping[str, int],
        foot: str,
    ) -> None:
        normalized_positions = tuple(
            normalize_role(position) for position in preferred_positions
        )
        if not 1 <= len(normalized_positions) <= 3:
            raise ValueError(f"{name} must have between 1 and 3 preferred positions.")

        normalized_attributes = {
            attribute.lower(): int(score) for attribute, score in attributes.items()
        }

        try:
            normalized_foot = normalize_foot(foot)
        except ValueError as error:
            raise ValueError(f"{name} has an invalid foot value: {foot!r}") from error

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "preferred_positions", normalized_positions)
        object.__setattr__(self, "attributes", normalized_attributes)
        object.__setattr__(self, "foot", normalized_foot)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Player":
        return cls(
            name=data["name"],
            preferred_positions=tuple(data["preferred_positions"]),
            attributes=data["attributes"],
            foot=data["foot"],
        )


@dataclass(frozen=True)
class AssignmentResult:
    slot: FormationSlot
    player: Player
    score: AssignmentBreakdown


@dataclass(frozen=True)
class LineupSolution:
    formation_name: str
    assignments: tuple[AssignmentResult, ...]
    total_score: int
    solver_status: str
