from twophase import solve

def convert_to_kociemba(cube_json):
    """
    Convert cube state JSON to Kociemba string format.
    The order must be URFDLB (Up, Right, Front, Down, Left, Back)
    """
    # Define color mapping based on center pieces
    # This assumes standard color scheme where:
    # Up (White), Right (Red), Front (Green), Down (Yellow), Left (Orange), Back (Blue)
    color_map = {
        'WHITE': 'U',
        'RED': 'R',
        'GREEN': 'F',
        'YELLOW': 'D',
        'ORANGE': 'L',
        'BLUE': 'B'
    }
    
    # The order we need to process faces
    face_order = ['up', 'right', 'front', 'down', 'left', 'back']
    
    # Function to get sorted positions for a face
    def get_sorted_positions(face_data):
        # Convert positions to array for easier sorting
        positions = []
        for pos, color in face_data.items():
            col, row = map(int, pos.split(','))
            positions.append((row, col, color))
        
        # Sort by row then column
        positions.sort()
        return [color for _, _, color in positions]
    
    # Build Kociemba string
    kociemba_string = ''
    for face in face_order:
        face_colors = get_sorted_positions(cube_json[face])
        for color in face_colors:
            kociemba_string += color_map[color]
    
    return kociemba_string

# Test with provided JSON
test_cube = {
   "up": {
      "0,0": "WHITE", "1,0": "ORANGE", "2,0": "BLUE",
      "0,1": "RED", "1,1": "BLUE", "2,1": "BLUE",
      "0,2": "BLUE", "1,2": "BLUE", "2,2": "RED"
   },
   "right": {
      "0,0": "YELLOW", "1,0": "WHITE", "2,0": "WHITE",
      "0,1": "GREEN", "1,1": "YELLOW", "2,1": "GREEN",
      "0,2": "GREEN", "1,2": "BLUE", "2,2": "YELLOW"
   },
   "front": {
      "0,0": "WHITE", "1,0": "ORANGE", "2,0": "GREEN",
      "0,1": "ORANGE", "1,1": "RED", "2,1": "WHITE",
      "0,2": "BLUE", "1,2": "YELLOW", "2,2": "WHITE"
   },
   "down": {
      "0,0": "ORANGE", "1,0": "GREEN", "2,0": "ORANGE",
      "0,1": "RED", "1,1": "GREEN", "2,1": "YELLOW",
      "0,2": "ORANGE", "1,2": "WHITE", "2,2": "BLUE"
   },
   "left": {
      "0,0": "RED", "1,0": "WHITE", "2,0": "ORANGE",
      "0,1": "BLUE", "1,1": "WHITE", "2,1": "GREEN",
      "0,2": "YELLOW", "1,2": "YELLOW", "2,2": "YELLOW"
   },
   "back": {
      "0,0": "GREEN", "1,0": "YELLOW", "2,0": "RED",
      "0,1": "RED", "1,1": "ORANGE", "2,1": "RED",
      "0,2": "GREEN", "1,2": "ORANGE", "2,2": "RED"
   }
}

# Print the resulting string
result = convert_to_kociemba(test_cube)
print(f"Kociemba string: {result}")

# Print each face to verify correct ordering
for face in ['up', 'right', 'front', 'down', 'left', 'back']:
    print(f"\n{face.upper()} face:")
    face_data = test_cube[face]
    rows = [[' ' for _ in range(3)] for _ in range(3)]
    for pos, color in face_data.items():
        col, row = map(int, pos.split(','))
        rows[row][col] = color[0]
    for row in rows:
        print(' '.join(row))

solution = solve(result)
print(f"Solution: {solution}")

