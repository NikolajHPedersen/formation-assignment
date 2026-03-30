from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model

from data_class import AssignmentBreakdown, AssignmentResult, FormationSlot, LineupSolution, Player, normalize_role


# TODO: FORMATION_TEMPLATES should be loaded from db or api. ROLE_ATTRIBUTE_WEIGHTS should be associated to each formation.
# TODO: Hyperparameters (sidefootpreference, ...) should be tweakable.
FORMATION_TEMPLATES: dict[str, tuple[str, ...]] = {
    "4-3-3": ("GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"),
    "4-2-3-1": ("GK", "LB", "CB", "CB", "RB", "CM", "CM", "LW", "CAM", "RW", "ST"),
    "4-4-2": ("GK", "LB", "CB", "CB", "RB", "LM", "CM", "CM", "RM", "ST", "ST"),
    "1-4-1": ("GK", "CM", "CM", "CM", "CM", "ST"),
}
# MOCK
ROLE_ATTRIBUTE_WEIGHTS: dict[str, dict[str, int]] = {
    "GK": {"goalkeeping": 8, "passing": 2},
    "LB": {"pace": 3, "passing": 2, "dribbling": 1, "defending": 4, "physical": 2},
    "RB": {"pace": 3, "passing": 2, "dribbling": 1, "defending": 4, "physical": 2},
    "CB": {"pace": 1, "passing": 1, "defending": 5, "physical": 4},
    "CDM": {"passing": 3, "dribbling": 1, "defending": 4, "physical": 2},
    "CM": {"pace": 1, "shooting": 1, "passing": 4, "dribbling": 2, "defending": 2, "physical": 1},
    "CAM": {"pace": 1, "shooting": 2, "passing": 4, "dribbling": 4},
    "LM": {"pace": 3, "shooting": 1, "passing": 3, "dribbling": 3},
    "RM": {"pace": 3, "shooting": 1, "passing": 3, "dribbling": 3},
    "LW": {"pace": 4, "shooting": 2, "passing": 2, "dribbling": 4},
    "RW": {"pace": 4, "shooting": 2, "passing": 2, "dribbling": 4},
    "ST": {"pace": 3, "shooting": 5, "dribbling": 1, "physical": 2},
    "LWB": {"pace": 3, "passing": 2, "dribbling": 2, "defending": 3, "physical": 2},
    "RWB": {"pace": 3, "passing": 2, "dribbling": 2, "defending": 3, "physical": 2},
}
# MOCK
SIDE_FOOT_PREFERENCE: dict[str, str] = {
    "LB": "left",
    "LWB": "left",
    "LM": "left",
    "LW": "right",
    "RB": "right",
    "RWB": "right",
    "RM": "right",
    "RW": "left",
}

PREFERENCE_POINTS = {
    0: 40,  # first preferred position
    1: 24,
    2: 10,
}

UNLISTED_POSITION_PENALTY = -12
NATURAL_FOOT_BONUS = 8
WRONG_FOOT_PENALTY = -5

STATUS_NAMES = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.MODEL_INVALID: "MODEL_INVALID",
    cp_model.UNKNOWN: "UNKNOWN",
}

AssignmentKey = tuple[int, int]  # the player index and the slot index


def safe_name(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")


def build_formation_slots(formation_name: str) -> list[FormationSlot]:
    template = FORMATION_TEMPLATES.get(formation_name)
    if template is None:  # hvis formationen ikke er lavet/findes
        supported = ", ".join(sorted(FORMATION_TEMPLATES))
        raise ValueError(f"Unsupported formation {formation_name!r}. Supported formations: {supported}")

    role_counts: defaultdict[str, int] = defaultdict(int)
    slots: list[FormationSlot] = []
    for role in template:
        normalized_role = normalize_role(role)
        role_counts[normalized_role] += 1  # tæller hvor mange gange en rolle optræder i formationen
        slots.append(
            FormationSlot(  # laver en slot for hver rolle i formationen
                slot_id=f"{normalized_role}{role_counts[normalized_role]}",  # slot_id er rolen + antallet af gange den optræder i formationen
                role=normalized_role,
            )
        )
    return slots


def preference_score(player: Player, role: str) -> int:
    for rank in range(len(player.preferred_positions)):
        preferred_role = player.preferred_positions[rank]
        if preferred_role == role:
            return PREFERENCE_POINTS.get(rank, 0)
    return UNLISTED_POSITION_PENALTY


def attribute_score(player: Player, role: str) -> int:
    attribute_weights = ROLE_ATTRIBUTE_WEIGHTS.get(role)
    if attribute_weights is None:
        return 0

    total_weight = sum(attribute_weights.values())
    weighted_sum = 0

    for attribute, weight in attribute_weights.items():
        weighted_sum += player.attributes.get(attribute, 0) * weight
    weighted_average = int(round(weighted_sum / total_weight))
    return weighted_average


def footedness_score(player: Player, role: str) -> int:
    preferred_foot = SIDE_FOOT_PREFERENCE.get(role)
    if preferred_foot is None:
        return 0
    if player.foot == preferred_foot:
        return NATURAL_FOOT_BONUS
    return WRONG_FOOT_PENALTY


def build_assignment_breakdown(player: Player, slot: FormationSlot) -> AssignmentBreakdown:
    preference = preference_score(player, slot.role)
    attributes = attribute_score(player, slot.role)
    footedness = footedness_score(player, slot.role)
    return AssignmentBreakdown(
        preference=preference,
        attributes=attributes,
        footedness=footedness,
        total=preference + attributes + footedness,
    )


def build_players_from_data_file(data_dir: Path, file_name: str) -> list[Player]:
    data_path = data_dir / file_name
    with data_path.open(encoding="utf-8") as file:
        player_data_list = json.load(file)
    return [Player.from_dict(player_data) for player_data in player_data_list]


# returnerer en dict med assignment breakdown (preference, attributes, footedness, total) for hver player og slot
def _build_score_lookup(players: list[Player], slots: list[FormationSlot]) -> dict[AssignmentKey, AssignmentBreakdown]:
    return {
        (player_index, slot_index): build_assignment_breakdown(player, slot)
        for player_index, player in enumerate[Player](players)
        for slot_index, slot in enumerate[FormationSlot](slots)
    }


def _create_assignment_vars(model: cp_model.CpModel, players: list[Player], slots: list[FormationSlot]) -> dict[AssignmentKey, cp_model.IntVar]:
    return {  # laver en dict med assignment vars for hver player og slot
        (player_index, slot_index): model.new_bool_var(f"assign_{safe_name(player.name)}_to_{slot.slot_id.lower()}")
        for player_index, player in enumerate[Player](players)
        for slot_index, slot in enumerate[FormationSlot](slots)
    }


def _add_assignment_constraints(
    model: cp_model.CpModel,
    players: list[Player],
    slots: list[FormationSlot],
    assignment_vars: dict[AssignmentKey, cp_model.IntVar],  # dict med assignment vars for hver player og slot
) -> None:
    for slot_index in range(len(slots)):
        vars_for_slot = []
        for player_index in range(len(players)):
            vars_for_slot.append(assignment_vars[player_index, slot_index])
        model.add_exactly_one(vars_for_slot)  # tilføjer en constraint således at hver slot har en player

    for player_index in range(len(players)):
        vars_for_player = []
        for slot_index in range(len(slots)):
            vars_for_player.append(assignment_vars[player_index, slot_index])
        model.add_at_most_one(vars_for_player)  # tilføjer en constraint således at hver player har højst én slot


def _extract_assignments(
    solver: cp_model.CpSolver,
    players: list[Player],
    slots: list[FormationSlot],
    assignment_vars: dict[AssignmentKey, cp_model.IntVar],
    score_lookup: dict[AssignmentKey, AssignmentBreakdown],
) -> tuple[AssignmentResult, ...]:
    assignments: list[AssignmentResult] = []
    for slot_index, slot in enumerate[FormationSlot](slots):
        for player_index, player in enumerate[Player](players):
            if solver.value(assignment_vars[player_index, slot_index]) != 1:
                continue
            assignments.append(
                AssignmentResult(
                    slot=slot,
                    player=player,
                    score=score_lookup[player_index, slot_index],
                )
            )
            break
    return tuple(assignments)


def solve_lineup(players: list[Player], formation_name: str) -> LineupSolution:
    slots = build_formation_slots(formation_name)
    if len(players) < len(slots):
        raise ValueError(f"The squad needs at least {len(slots)} players for formation {formation_name}.")

    model = cp_model.CpModel()  # modellen som skal løses
    score_lookup = _build_score_lookup(players, slots)
    assignment_vars = _create_assignment_vars(model, players, slots)
    _add_assignment_constraints(model, players, slots, assignment_vars)  # tilføjer constraints til modellen

    objective_terms = []
    for player_index in range(len(players)):
        for slot_index in range(len(slots)):
            objective_terms.append(score_lookup[player_index, slot_index].total * assignment_vars[player_index, slot_index])
    model.maximize(sum(objective_terms))  # maksimerer total score

    solver = cp_model.CpSolver()
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"No valid lineup found. Solver status: {STATUS_NAMES.get(status, str(status))}")

    assignments = _extract_assignments(solver, players, slots, assignment_vars, score_lookup)
    return LineupSolution(
        formation_name=formation_name,
        assignments=assignments,
        total_score=sum(assignment.score.total for assignment in assignments),
        solver_status=STATUS_NAMES.get(status, str(status)),
    )


def format_solution(solution: LineupSolution, players: list[Player]) -> str:
    used_players = set()
    for assignment in solution.assignments:
        used_players.add(assignment.player.name)
    unused_names = []
    for player in players:
        if player.name not in used_players:
            unused_names.append(player.name)
    if unused_names:
        unused_players = ", ".join(unused_names)
    else:
        unused_players = "none"

    lines = [
        f"Formation: {solution.formation_name}",
        f"Solver status: {solution.solver_status}",
        "",
        "Starting lineup:",
    ]
    lines.extend(
        (
            f"  {assignment.slot.slot_id:>3} -> {assignment.player.name:<16}"
            f" total={assignment.score.total:>3}"
            f" (pref={assignment.score.preference:>3},"
            f" attr={assignment.score.attributes:>3},"
            f" foot={assignment.score.footedness:>3})"
        )
        for assignment in solution.assignments
    )
    lines.extend(
        [
            "",
            f"Total score: {solution.total_score}",
            f"Unused squad players: {unused_players}",
        ]
    )
    return "\n".join(lines)
