import json
from twophase import solve

# Read cube state from JSON
with open('Tester.json', 'r') as f:
    cube_state = json.load(f)

# Convert cube state to Kociemba string
def json_to_kociemba(cube_json):
    color_map = {'WHITE': 'U', 'RED': 'R', 'GREEN': 'F', 
                 'YELLOW': 'D', 'ORANGE': 'L', 'BLUE': 'B'}

    kociemba_string = ""
    for face in ['top', 'right', 'front', 'bottom', 'left', 'back']:
        for x in range(3):
            for y in range(3):
                color = cube_json[face][f"{x},{y}"]
                kociemba_string += color_map[color]

    return kociemba_string

# Solve the cube
kociemba_string = json_to_kociemba(cube_state)
solution = solve(kociemba_string)

print(f"Solution: {solution}")
