from constraint import Problem, AllDifferentConstraint




players = [
    {"name": "Alisson", "pos_prefs": {"GK": 1}, "foot": "Right"},
    {"name": "Nikolaj", "pos_prefs": {"LB": 1, }, "foot": "Right"},
    {"name": "Ederson", "pos_prefs": {"LB": 1}, "foot": "Left"},
    {"name": "Robertson", "pos_prefs": {"LB": 1, "LWB": 2}, "foot": "Left"},
    {"name": "Walker", "pos_prefs": {"RB": 1, "CB": 2}, "foot": "Right"},
    {"name": "Van Dijk", "pos_prefs": {"CB": 1}, "foot": "Right"},
    {"name": "Salah", "pos_prefs": {"RW": 1, "ST": 2}, "foot": "Left"},
    {"name": "Haaland", "pos_prefs": {"ST": 1}, "foot": "Left"},
    {"name": "Trent", "pos_prefs": {"RB": 1, "CM": 2}, "foot": "Right"},
]

players2 = [
    {"name": "Alisson", "pos_prefs": {"GK": 1}, "foot": "Right"},
    {"name": "Nikolaj", "pos_prefs": {"B": 1, }, "foot": "Right"},
    {"name": "Ederson", "pos_prefs": {"B": 1}, "foot": "Left"},
    {"name": "Robertson", "pos_prefs": {"B": 1, "LWB": 2}, "foot": "Left"},
    {"name": "Walker", "pos_prefs": {"B": 1, "B": 2}, "foot": "Right"},
    {"name": "Van Dijk", "pos_prefs": {"B": 1}, "foot": "Right"},
    {"name": "Salah", "pos_prefs": {"RW": 1, "ST": 2}, "foot": "Left"},
    {"name": "Haaland", "pos_prefs": {"ST": 1}, "foot": "Left"},
    {"name": "Trent", "pos_prefs": {"RB": 1, "CM": 2}, "foot": "Right"},
]

formation_obj = {"GK":1,"LB":1,"RB":1,"CB":2,"CM":2,"RM":1,"LM":1,"ST":2}

formation = ["GK", "LB", "CB", "RB", "ST"]

problem = Problem()

for p in players:
    # Here the domain is the list of positions they CAN play
    problem.addVariable(p["name"], list(p["pos_prefs"].keys()))
    
#    for pos in list(p["pos_prefs"].keys()):
#        problem.addConstraint(pos,p["name"])

#def posConstraint(playerName):
#    return 


def leftOnly():
    print("not implemented")

def formation_constraint(*assigned_positions):
    required = set(formation) # Basic requirements for this example
    assigned_set = set(assigned_positions)
    # Check if all required positions are covered
    return required.issubset(assigned_set)

problem.addConstraint(formation_constraint, list([player["name"] for player in players]))

solutions = problem.getSolutions()

def calculate_score(solution):
    """Lower score is better (Total Rank Sum)"""
    total_rank = 0
    for p_name, pos  in solution.items():
        for player in players:
            if player["name"] == p_name:
                total_rank += player["pos_prefs"][pos]
                break
    return total_rank

# Sort solutions by the best priority match
optimized_solutions = sorted(solutions, key=calculate_score)


if optimized_solutions:
    for i in optimized_solutions:
        print(calculate_score(i))
    best = optimized_solutions[0]
    print(f"Best Lineup (Score: {calculate_score(best)}):")
    for pos, player in best.items():
        print(f"{pos}: {player}")
else:
    print("No valid lineup found with current constraints.")