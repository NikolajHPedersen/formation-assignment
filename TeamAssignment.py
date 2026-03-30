
from constraint import Problem, AllDifferentConstraint

players = [
    {"Id": 1,  "Lfoot": False, "Positions": ["ST",  "LCM", "GK"]},
    {"Id": 2,  "Lfoot": False, "Positions": ["RST", "RCM", "RCB"]},
    {"Id": 3,  "Lfoot": True,  "Positions": ["LST", "LCM", "LCB"]},
    {"Id": 4,  "Lfoot": False, "Positions": ["RST", "RCM", "RB"]},
    {"Id": 5,  "Lfoot": True,  "Positions": ["LST", "LM",  "LB"]},
    {"Id": 6,  "Lfoot": False, "Positions": ["RST", "RM",  "RB"]},
    {"Id": 7,  "Lfoot": False, "Positions": ["ST",  "RCM", "RCB"]},
    {"Id": 8,  "Lfoot": False, "Positions": ["ST",  "LCM", "LCB"]},
    {"Id": 9,  "Lfoot": True,  "Positions": ["LST", "LM",  "LCB"]},
    {"Id": 10, "Lfoot": False, "Positions": ["RST", "RM",  "RCB"]},
    {"Id": 11, "Lfoot": True,  "Positions": ["LST", "LM",  "LB"]},
    {"Id": 12, "Lfoot": False, "Positions": ["RST", "RM",  "RB"]},
    {"Id": 13, "Lfoot": True,  "Positions": ["LST", "LCM", "LCB"]},
    {"Id": 14, "Lfoot": False, "Positions": ["RST", "RCM", "RCB"]},
    {"Id": 15, "Lfoot": True,  "Positions": ["LST", "LM",  "LB"]},
    {"Id": 16, "Lfoot": False, "Positions": ["RST", "RM",  "RB"]},
    {"Id": 17, "Lfoot": False, "Positions": ["ST",  "RCM", "RB"]},
    {"Id": 18, "Lfoot": True,  "Positions": ["ST",  "LCM", "LB"]},
    {"Id": 19, "Lfoot": False, "Positions": ["RST", "RCM", "RCB"]},
    {"Id": 20, "Lfoot": True,  "Positions": ["LST", "LCM", "LCB"]},
]

# Each slot has a capacity — how many players it needs
formation_slots = {
    "GK":  {"capacity": 1, "players": []},
    "LB":  {"capacity": 1, "players": []},
    "RB":  {"capacity": 1, "players": []},
    "LCB": {"capacity": 1, "players": []},
    "RCB": {"capacity": 1, "players": []},
    "LCM": {"capacity": 1, "players": []},
    "RCM": {"capacity": 1, "players": []},
    "LM":  {"capacity": 1, "players": []},
    "RM":  {"capacity": 1, "players": []},
    "LST": {"capacity": 1, "players": []},
    "RST": {"capacity": 1, "players": []},
}

# Expand slots by capacity — a slot needing 2 players becomes slot_0 and slot_1
expanded_slots = []
for slot, info in formation_slots.items():
    for i in range(info["capacity"]):
        expanded_slots.append(f"{slot}_{i}" if info["capacity"] > 1 else slot)

# Build slot → eligible player IDs mapping
def get_eligible(slot_name):
    base = slot_name.split("_")[0]  # strip _0, _1 suffix if present
    return [p["Id"] for p in players if base in p["Positions"]]

# --- Build the problem ---
problem = Problem()

for slot in expanded_slots:
    eligible = get_eligible(slot)
    if not eligible:
        print(f"WARNING: no player can fill {slot}")
    problem.addVariable(slot, eligible)

# No player assigned to more than one slot
problem.addConstraint(AllDifferentConstraint(), expanded_slots)

# --- Score: preference rank, lower is better ---
def calculate_score(solution):
    total = 0
    for slot, player_id in solution.items():
        player = next(p for p in players if p["Id"] == player_id)
        base = slot.split("_")[0]
        rank = player["Positions"].index(base)
        total += rank
    return total

# --- Solve ---
print("Solving...\n")
solutions = problem.getSolutions()
print(f"Found {len(solutions)} valid lineups\n")

if solutions:
    best = sorted(solutions, key=calculate_score)[0]
    score = calculate_score(best)

    # Collect starting XI player IDs
    starting_ids = set(best.values())

    # Build substitutes list
    substitutes = [p for p in players if p["Id"] not in starting_ids]

    print(f"Starting XI (preference score: {score}):")
    print(f"{'Slot':<8} {'Player ID':<12} {'Preference'}")
    print("-" * 35)
    for slot, player_id in sorted(best.items()):
        player = next(p for p in players if p["Id"] == player_id)
        base = slot.split("_")[0]
        rank = player["Positions"].index(base)
        pref_label = ["1st", "2nd", "3rd"][rank]
        print(f"  {slot:<8} Player {player_id:<6} {pref_label} choice")

    print(f"\nSubstitutes ({len(substitutes)} players):")
    print("-" * 35)
    for p in substitutes:
        print(f"  Player {p['Id']:<4} can play: {', '.join(p['Positions'])}")
else:
    print("No valid lineup found.")