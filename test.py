def convert_to_kociemba(cube_json):
    """
    Convert cube state JSON to Kociemba string format with standard color mapping:
    - White: U (up)
    - Red: R (right)
    - Green: F (front)
    - Yellow: D (down)
    - Orange: L (left)
    - Blue: B (back)
    """
    # Use standard color mapping
    color_map = {
        'WHITE': 'U',
        'RED': 'R',
        'GREEN': 'F',
        'YELLOW': 'D',
        'ORANGE': 'L',
        'BLUE': 'B'
    }
    
    def get_face_colors(face_data):
        """Get colors for a face in Kociemba order"""
        result = []
        # Read in Kociemba order (top-to-bottom, left-to-right)
        for row in range(3):
            for col in range(3):
                pos = f"{col},{row}"
                color = face_data[pos]
                mapped_color = color_map[color]
                result.append(mapped_color)
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

if __name__ == "__main__":
    import json
    from twophase import solve
    
    # Load test1.json
    with open('test1.json', 'r') as f:
        cube_json = json.load(f)
    
    # Print original state
    print("Original Cube State:")
    print_cube_state(cube_json)
    
    # Convert to Kociemba string
    kociemba_str = convert_to_kociemba(cube_json)
    print("\nKociemba string:", kociemba_str)
    
    # Show the face-by-face interpretation
    print("\nKociemba interpretation:")
    faces = ['U', 'R', 'F', 'D', 'L', 'B']
    for i, face in enumerate(faces):
        print(f"\n{face} face:")
        face_str = kociemba_str[i*9:(i+1)*9]
        for j in range(0, 9, 3):
            print(face_str[j:j+3])
    
    # Try to solve
    try:
        solution = solve(kociemba_str)
        print("\nSolution found:", solution)
    except ValueError as e:
        print("\nError solving cube:", str(e))
