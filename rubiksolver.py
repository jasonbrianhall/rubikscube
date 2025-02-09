from twophase import solve
import threading
import os
from pathlib import Path
import traceback

def get_tables_path():
    """Get the path to the tables.json file in the user's home directory"""
    home = str(Path.home())
    rubiksolver_dir = os.path.join(home, '.rubiksolver')
    return os.path.join(rubiksolver_dir, 'tables.json')


def get_center_colors(cube_json):
    """
    Extract center color of each face from the cube state.
    Returns a dictionary mapping face positions to their center colors.
    """
    centers = {}
    for face in ['up', 'right', 'front', 'down', 'left', 'back']:
        # Center piece is always at position 1,1
        center_color = cube_json[face]['1,1']
        centers[face] = center_color
    return centers

def create_dynamic_color_mapping(centers):
    """
    Create a color-to-face mapping based on actual cube orientation.
    Standard Kociemba orientation requires:
    - White center on top (U)
    - Green center on front (F)
    """
    # First, create mapping of actual positions to Kociemba faces
    position_to_kociemba = {
        'up': 'U',
        'right': 'R',
        'front': 'F',
        'down': 'D',
        'left': 'L',
        'back': 'B'
    }
    
    # Create dynamic color mapping based on center positions
    color_map = {}
    for position, color in centers.items():
        kociemba_face = position_to_kociemba[position]
        color_map[color] = kociemba_face
    
    return color_map

def convert_to_kociemba(cube_json):
    """
    Convert cube state JSON to Kociemba string format with dynamic color mapping
    based on actual cube orientation.
    """
    # Get center colors and create dynamic mapping
    centers = get_center_colors(cube_json)
    color_map = create_dynamic_color_mapping(centers)
    
    def get_face_colors(face_data):
        """Get colors for a face in Kociemba order"""
        result = []
        # Read in Kociemba order (top-to-bottom, left-to-right)
        for row in range(3):
            for col in range(3):
                pos = f"{col},{row}"
                color = face_data[pos]
                mapped_face = color_map[color]
                result.append(mapped_face)
        return ''.join(result)
    
    # Build Kociemba string in URFDLB order
    kociemba_string = ''
    for face in ['up', 'right', 'front', 'down', 'left', 'back']:
        face_string = get_face_colors(cube_json[face])
        kociemba_string += face_string
    
    return kociemba_string

def print_cube_state(cube_json):
    """Print the cube state for verification"""
    for face in ['up', 'right', 'front', 'down', 'left', 'back']:
        print(f"\n{face.upper()} face:")
        grid = [['' for _ in range(3)] for _ in range(3)]
        for pos, color in cube_json[face].items():
            col, row = map(int, pos.split(','))
            grid[row][col] = color[0]
        for row in grid:
            print(' '.join(row))
            
def print_centers(cube_json):
    """Print center colors for debugging orientation"""
    centers = get_center_colors(cube_json)
    print("\nCenter colors:")
    for face, color in centers.items():
        print(f"{face}: {color}")

def solve_in_thread(kociemba_str, result):
    try:
        result[0] = solve(kociemba_str)
    except Exception as e:
        print(traceback.format_exc())
        result[0] = None

def solve_cube(cube_state):

    exists = os.path.exists(get_tables_path())
    if not exists:
        print("Tables.json needs generated.  This could take up to a minute so please be patient.")
    kociemba_str = convert_to_kociemba(cube_state)
    print(f"\nKociemba string: {kociemba_str}\n")
    
    result = [None]
    solver_thread = threading.Thread(target=solve_in_thread, args=(kociemba_str, result))
    solver_thread.start()
    solver_thread.join()
    
    solution = result[0]
    if solution:
        print(f"Solution: {solution}")
    else:
        print("No solution found")
    return solution

def troubleshoot_cube_string(kociemba_str):
    """
    Analyzes a Kociemba string to check if it's solved, count colors, and validate corners.
    
    Args:
        kociemba_str (str): The Kociemba string to analyze
        
    Returns:
        str: "Already solved" if solved, otherwise counts and corner validation
    """
    print(kociemba_str)

    # Check if already solved
    # In a solved cube, each face should be 9 of the same letter
    face_size = 9
    faces = [
        kociemba_str[0:9],          # U face
        kociemba_str[9:18],         # R face
        kociemba_str[18:27],        # F face
        kociemba_str[27:36],        # D face
        kociemba_str[36:45],        # L face
        kociemba_str[45:54]         # B face
    ]
    
    if kociemba_str=="UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
        return "Already solved"
    
    # Count occurrences
    counts = {
        'U': 0,  # White
        'R': 0,  # Red
        'F': 0,  # Green
        'D': 0,  # Yellow
        'L': 0,  # Orange
        'B': 0   # Blue
    }
    
    for char in kociemba_str.upper():
        if char in counts:
            counts[char] += 1
    
    # First check if we have exactly 9 of each color
    if not all(count == 9 for count in counts.values()):
        return f"U (White): {counts['U']}, R (Red): {counts['R']}, F (Green): {counts['F']}, D (Yellow): {counts['D']}, L (Orange): {counts['L']}, B (Blue): {counts['B']}"
    
    # If we have 9 of each, validate corners
    corner_triplets = []
    
    # UFR
    corner_triplets.append((
        kociemba_str[2],                    # U face
        kociemba_str[9],                    # R face
        kociemba_str[18]                    # F face
    ))
    
    # UFL
    corner_triplets.append((
        kociemba_str[0],                    # U face
        kociemba_str[18],                   # F face
        kociemba_str[36]                    # L face
    ))
    
    # UBL
    corner_triplets.append((
        kociemba_str[0],                    # U face
        kociemba_str[45],                   # B face
        kociemba_str[36]                    # L face
    ))
    
    # UBR
    corner_triplets.append((
        kociemba_str[2],                    # U face
        kociemba_str[47],                   # B face
        kociemba_str[9]                     # R face
    ))
    
    # DFR
    corner_triplets.append((
        kociemba_str[29],                   # D face
        kociemba_str[24],                   # F face
        kociemba_str[17]                    # R face
    ))
    
    # DFL
    corner_triplets.append((
        kociemba_str[27],                   # D face
        kociemba_str[24],                   # F face
        kociemba_str[44]                    # L face
    ))
    
    # DBL
    corner_triplets.append((
        kociemba_str[27],                   # D face
        kociemba_str[53],                   # B face
        kociemba_str[42]                    # L face
    ))
    
    # DBR
    corner_triplets.append((
        kociemba_str[29],                   # D face
        kociemba_str[53],                   # B face
        kociemba_str[17]                    # R face
    ))
    
    # Check for invalid corner combinations
    opposite_faces = {
        'U': 'D', 'D': 'U',
        'F': 'B', 'B': 'F',
        'L': 'R', 'R': 'L'
    }
    
    for corner in corner_triplets:
        # Check if any corner has same color twice
        if len(set(corner)) < 3:
            return f"U (White): {counts['U']}, R (Red): {counts['R']}, F (Green): {counts['F']}, D (Yellow): {counts['D']}, L (Orange): {counts['L']}, B (Blue): {counts['B']} - Invalid corners: same color appears multiple times on a corner"
        
        # Check if corner has opposite faces
        for i in range(3):
            for j in range(i + 1, 3):
                if corner[i] == opposite_faces[corner[j]]:
                    return f"U (White): {counts['U']}, R (Red): {counts['R']}, F (Green): {counts['F']}, D (Yellow): {counts['D']}, L (Orange): {counts['L']}, B (Blue): {counts['B']} - Invalid corners: opposite colors on same corner"
    
    return f"U (White): {counts['U']}, R (Red): {counts['R']}, F (Green): {counts['F']}, D (Yellow): {counts['D']}, L (Orange): {counts['L']}, B (Blue): {counts['B']} - Valid corners"
