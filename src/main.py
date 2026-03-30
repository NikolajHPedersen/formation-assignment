from __future__ import annotations

from pathlib import Path

from data_class import Player
from lineup import build_players_from_data_file, format_solution, solve_lineup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FORMATION_NAME = "4-3-3"
EXAMPLE_SQUADS: tuple[tuple[str, str], ...] = (
    ("barcelona_reference.json", "Barcelona reference"),
    ("cm_competions.json", "CM competitions"),
    ("weird_random_22_player_test.json", "Weird random 22-player test"),
    ("not_enough_players_failure_case.json", "Not enough players failure case"),
)


def run_example(example_name: str, players: list[Player], formation_name: str) -> None:
    print(
        f"Example squad: {example_name}"
    )  # example name could be: "barcelona reference"
    try:
        solution = solve_lineup(players, formation_name)
    except (ValueError, RuntimeError) as error:
        print(f"Run failed: {error}")
        return

    print(format_solution(solution, players))


def load_example_squads() -> list[tuple[str, list[Player]]]:
    squads = []
    for file_name, example_name in EXAMPLE_SQUADS:
        players = build_players_from_data_file(DATA_DIR, file_name)
        squads.append((example_name, players))
    return squads


# TODO: make a func that loads from a query db or api


def main() -> None:
    for index, (example_name, players) in enumerate(load_example_squads()):
        if index:
            print()
            print("=" * 72)
            print()
        run_example(example_name, players, FORMATION_NAME)


if __name__ == "__main__":
    main()
