from constraint import Problem, AllDifferentConstraint

players2 = [
    {"name": "Alisson", "pos_prefs": ["GK","CM","ST"], "foot": "Right"},
    {"name": "Nikolaj", "pos_prefs": ["LW","RB","CM"], "foot": "Right"}, 
    {"name": "Ederson", "pos_prefs": ["RB","RW","LB"], "foot": "Left"},  
    {"name": "Robertson", "pos_prefs": ["LW","CM","CB"], "foot": "Left"},
    {"name": "Walker", "pos_prefs": ["RB","ST","GK"], "foot": "Right"},
    {"name": "Van Dijk", "pos_prefs": ["RB","LM","ST"], "foot": "Right"},
    {"name": "Salah", "pos_prefs": ["RW", "CB","LB"], "foot": "Left"},
    {"name": "Haaland", "pos_prefs": ["ST","RB","RM"], "foot": "Left"},
    {"name": "Trent", "pos_prefs": ["RB", "CM", "LW"], "foot": "Right"},
    {"name": "Messi", "pos_prefs": ["ST","CM","LB"],"foot": "Right"},
    {"name": "Ronaldo", "pos_prefs": ["ST","CB","CM"], "foot": "Left"},
    {"name": "Jordan", "pos_prefs": ["RM","LB", "LM"], "foot": "Left"},
    {"name": "A", "pos_prefs": ["LB","CB","LM"],"foot":"Right"},
    {"name": "B", "pos_prefs": ["CB","CM","ST"],"foot":"Right"}
]
'''
GK = Goal keeper
LB = Left back
RB = Right back
CB = Center back
CM = Center midfielder
RM = Right midfielder
LM = Left midfielder
ST = Striker
LW = Left wing
RW = Right wing
'''


formation_obj = {"GK":1,"LB":1,"RB":1,"CB":2,"CM":1,"RM":1,"LM":1,"ST":1, "LW":1, "RW":1}

def get_position_list(formation):
    return list(formation_obj.keys())

formation = ["GK", "LB", "CB", "RB", "ST"]

problem = Problem()

for p in players2:
    # Here the domain is the list of positions they CAN play
    problem.addVariable(p["name"], p["pos_prefs"])
    
#    for pos in list(p["pos_prefs"].keys()):
#        problem.addConstraint(pos,p["name"])

def new_formation_constraint(*assigned_positions):
    assigned = {}
    for key in list(formation_obj.keys()):
        assigned[key] = 0
    for pos in assigned_positions:
        assigned[pos] += 1
    return comp(assigned,formation_obj)

def comp(assigned, formation):
    for key in list(formation.keys()):
        if(assigned[key] < formation[key]):
            return False
    return True

#problem.addConstraint(formation_constraint, list([player["name"] for player in players]))
problem.addConstraint(new_formation_constraint, list([player["name"] for player in players2]))

solutions = problem.getSolutions()
print(f"found {len(solutions)} solutions")
def calculate_score(solution):
    """Lower score is better (Total Rank Sum)"""
    total_rank = 0
    for p_name, pos  in solution.items():
        for player in players2:
            if player["name"] == p_name:
                total_rank += 3 - linear_search(player["pos_prefs"], pos)
                if ("L" in pos and player["foot"] == "Left") or ("R" in pos and player["foot"] == "Right"):
                    total_rank += 2
                break
    return total_rank

def linear_search(array, element):
    i = 0
    for e in array:
        if(e == element):
            return i
        i += 1
    return -1

# Sort solutions by the best priority match
optimized_solutions = sorted(solutions, key=calculate_score)


if optimized_solutions:
    best = optimized_solutions[len(optimized_solutions)-1]
    print(f"Best Lineup (Score: {calculate_score(best)}):")
    for pos, player in best.items():
        print(f"{pos}: {player}")
else:
    print("No valid lineup found with current constraints.")