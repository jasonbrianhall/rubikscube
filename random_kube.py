import random
import json
import sys

SOLVED = list("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")

COLOR_MAP = {
    'U': 'WHITE',
    'D': 'YELLOW',
    'F': 'RED',
    'B': 'ORANGE',
    'L': 'GREEN',
    'R': 'BLUE',
}

MOVES = {
    "U":  [(0,6,8,2), (1,3,7,5), (18,36,45,9), (19,37,46,10), (20,38,47,11)],
    "U'": [(0,2,8,6), (1,5,7,3), (18,9,45,36), (19,10,46,37), (20,11,47,38)],
    "U2": [(0,8), (2,6), (1,7), (3,5),
           (18,45), (19,46), (20,47),
           (9,36), (10,37), (11,38)],
    "D":  [(45,47,53,51), (46,48,52,50),
           (15,33,42,24), (16,34,43,25), (17,35,44,26)],
    "D'": [(45,51,53,47), (46,50,52,48),
           (15,24,42,33), (16,25,43,34), (17,26,44,35)],
    "D2": [(45,53), (47,51), (46,52), (48,50),
           (15,42), (16,43), (17,44),
           (24,33), (25,34), (26,35)],
    "L":  [(36,38,44,42), (37,41,43,39),
           (0,18,45,53), (3,21,48,50), (6,24,51,47)],
    "L'": [(36,42,44,38), (37,39,43,41),
           (0,53,45,18), (3,50,48,21), (6,47,51,24)],
    "L2": [(36,44), (38,42), (37,43), (39,41),
           (0,45), (3,48), (6,51),
           (18,53), (21,50), (24,47)],
    "R":  [(9,11,17,15), (10,14,16,12),
           (2,29,47,20), (5,32,50,23), (8,35,53,26)],
    "R'": [(9,15,17,11), (10,12,16,14),
           (2,20,47,29), (5,23,50,32), (8,26,53,35)],
    "R2": [(9,17), (11,15), (10,16), (12,14),
           (2,47), (5,50), (8,53),
           (20,29), (23,32), (26,35)],
    "F":  [(18,20,26,24), (19,23,25,21),
           (6,27,45,17), (7,30,46,14), (8,33,47,11)],
    "F'": [(18,24,26,20), (19,21,25,23),
           (6,17,45,27), (7,14,46,30), (8,11,47,33)],
    "F2": [(18,26), (20,24), (19,25), (21,23),
           (6,45), (7,46), (8,47),
           (17,27), (14,30), (11,33)],
    "B":  [(27,29,35,33), (28,32,34,30),
           (0,9,53,44), (1,12,52,41), (2,15,51,38)],
    "B'": [(27,33,35,29), (28,30,34,32),
           (0,44,53,9), (1,41,52,12), (2,38,51,15)],
    "B2": [(27,35), (29,33), (28,34), (30,32),
           (0,53), (1,52), (2,51),
           (9,44), (12,41), (15,38)],
}

ALL_MOVES = list(MOVES.keys())

def apply_move(cube, move):
    cube = cube[:]
    for cycle in MOVES[move]:
        if len(cycle) == 2:
            a, b = cycle
            cube[a], cube[b] = cube[b], cube[a]
        else:
            a, b, c, d = cycle
            cube[a], cube[b], cube[c], cube[d] = cube[d], cube[a], cube[b], cube[c]
    return cube

def cube_to_json(cube):
    """Convert flat 54-char cube to JSON - simple direct mapping"""
    faces = {
        'up': {},
        'right': {},
        'front': {},
        'down': {},
        'left': {},
        'back': {},
    }
    
    face_names = ['up', 'right', 'front', 'down', 'left', 'back']
    
    for face_idx, face_name in enumerate(face_names):
        start = face_idx * 9
        for i in range(9):
            col = i % 3
            row = i // 3
            sticker = cube[start + i]
            color = COLOR_MAP[sticker]
            faces[face_name][f"{col},{row}"] = color
    
    return faces

def apply_scramble(cube, scramble_str):
    """Apply a scramble string like 'U R F D' to the cube"""
    moves = scramble_str.split()
    for move in moves:
        if move not in MOVES:
            print(f"Warning: Unknown move '{move}'")
            continue
        cube = apply_move(cube, move)
    return cube

def save_cube(cube, scramble, filename_base="cube"):
    flat_file = f"{filename_base}.txt"
    with open(flat_file, 'w') as f:
        f.write(f"Scramble: {scramble}\n")
        f.write(f"State: {''.join(cube)}\n")
    print(f"Saved flat format to {flat_file}")
    
    json_file = f"{filename_base}.json"
    with open(json_file, 'w') as f:
        json.dump(cube_to_json(cube), f, indent=3)
    print(f"Saved JSON format to {json_file}")

if len(sys.argv) > 1:
    arg = sys.argv[1]
    
    # Check if it's a number (random moves) or a scramble string
    if arg.isdigit():
        num_moves = int(arg)
        cube = SOLVED[:]
        scramble = []
        last_face = None
        
        for _ in range(num_moves):
            while True:
                move = random.choice(ALL_MOVES)
                face = move[0]
                if face != last_face:
                    scramble.append(move)
                    last_face = face
                    break
            cube = apply_move(cube, move)
        
        scramble_str = " ".join(scramble)
        print(f"Generated cube with {num_moves} random moves")
    else:
        # Treat as scramble string
        scramble_str = arg
        cube = SOLVED[:]
        cube = apply_scramble(cube, scramble_str)
        print(f"Applied scramble: {scramble_str}")
else:
    # Default: 25 random moves
    num_moves = 25
    cube = SOLVED[:]
    scramble = []
    last_face = None
    
    for _ in range(num_moves):
        while True:
            move = random.choice(ALL_MOVES)
            face = move[0]
            if face != last_face:
                scramble.append(move)
                last_face = face
                break
        cube = apply_move(cube, move)
    
    scramble_str = " ".join(scramble)
    print(f"Generated cube with {num_moves} random moves")

print("Scramble:", scramble_str)
print("Cube state (flat):", "".join(cube))
print()
save_cube(cube, scramble_str)
