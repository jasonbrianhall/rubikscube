from twophase import solve
import threading

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
        result[0] = None

def solve_cube(cube_state):
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
    
    
