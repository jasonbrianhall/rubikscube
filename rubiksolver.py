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

def troubleshoot_cube_string(cube_str):
    """
    Analyzes a cube's state, counting colors and validating structure.
    First counts all colors, then validates corners if counts are correct.
    
    Args:
        cube_str (dict): The cube state dictionary
        
    Returns:
        str: Color counts and validation results
    """
    try:
        # Initialize color counts
        color_counts = {}
        
        # First pass - collect all unique colors and initialize counts
        for face in cube_str.values():
            for color in face.values():
                if color not in color_counts:
                    color_counts[color] = 0
                    
        # Second pass - count occurrences
        for face in cube_str.values():
            for color in face.values():
                color_counts[color] += 1
        
        # Build result string
        result_parts = []
        for color, count in sorted(color_counts.items()):
            result_parts.append(f"{color.capitalize()}: {count}")
        
        color_status = " ".join(result_parts)
        
        # Check if we have exactly 9 of each main color and 0 unassigned
        expected_colors = {'WHITE', 'RED', 'GREEN', 'YELLOW', 'ORANGE', 'BLUE'}
        if ('UNASSIGNED' not in color_counts and 
            all(color in color_counts for color in expected_colors) and
            all(color_counts[color] == 9 for color in expected_colors)):
            
            # If counts are good, convert to Kociemba and check corners
            kociemba_str = convert_to_kociemba(cube_str)
            
            # Check if already solved
            if kociemba_str == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
                return "Already solved"
                
            # Validate corners
            corner_triplets = [
                (kociemba_str[2], kociemba_str[9], kociemba_str[18]),    # UFR
                (kociemba_str[0], kociemba_str[18], kociemba_str[36]),   # UFL
                (kociemba_str[0], kociemba_str[45], kociemba_str[36]),   # UBL
                (kociemba_str[2], kociemba_str[47], kociemba_str[9]),    # UBR
                (kociemba_str[29], kociemba_str[24], kociemba_str[17]),  # DFR
                (kociemba_str[27], kociemba_str[24], kociemba_str[44]),  # DFL
                (kociemba_str[27], kociemba_str[53], kociemba_str[42]),  # DBL
                (kociemba_str[29], kociemba_str[53], kociemba_str[17])   # DBR
            ]
            
            opposite_faces = {
                'U': 'D', 'D': 'U',
                'F': 'B', 'B': 'F',
                'L': 'R', 'R': 'L'
            }
            
            for corner in corner_triplets:
                # Check for duplicate colors in corner
                if len(set(corner)) < 3:
                    return f"Invalid corners: same color appears multiple times on a corner"
                
                # Check for opposite colors in corner
                for i in range(3):
                    for j in range(i + 1, 3):
                        if corner[i] == opposite_faces[corner[j]]:
                            return f"Invalid corners: opposite colors on same corner"
            
            return f"{color_status} - Valid corners (this should have a solution)"
            
        return color_status
        
    except Exception as e:
        print(traceback.format_exc())
        return f"Error analyzing cube: {str(e)}"

