import json
from twophase import solve

def rotate_face_clockwise(face_data):
    """Rotate a face 90 degrees clockwise"""
    new_face = {}
    mapping = {
        "0,0": "2,0", "1,0": "2,1", "2,0": "2,2",
        "0,1": "1,0", "1,1": "1,1", "2,1": "1,2",
        "0,2": "0,0", "1,2": "0,1", "2,2": "0,2"
    }
    for old_pos, new_pos in mapping.items():
        new_face[new_pos] = face_data[old_pos]
    return new_face

def rotate_face_counterclockwise(face_data):
    """Rotate a face 90 degrees counterclockwise"""
    new_face = {}
    mapping = {
        "0,0": "0,2", "1,0": "0,1", "2,0": "0,0",
        "0,1": "1,2", "1,1": "1,1", "2,1": "1,0",
        "0,2": "2,2", "1,2": "2,1", "2,2": "2,0"
    }
    for old_pos, new_pos in mapping.items():
        new_face[new_pos] = face_data[old_pos]
    return new_face

def transform_cube(cube_data):
    """Transform the cube to match Kociemba orientation"""
    new_cube = {}
    
    # In your JSON format, we need to:
    # 1. Move the blue face (currently top) to front
    # 2. Move the red face (currently front) to right
    # 3. Move the white face (currently left) to top
    
    new_cube['front'] = cube_data['top']  # Blue center
    new_cube['right'] = cube_data['front']  # Red center
    new_cube['top'] = cube_data['left']  # White center
    new_cube['left'] = cube_data['back']  # Orange center
    new_cube['back'] = cube_data['right']  # Green center
    new_cube['bottom'] = cube_data['bottom']  # Yellow center
    
    # We also need to rotate some faces to maintain correct orientation
    new_cube['left'] = rotate_face_clockwise(new_cube['left'])
    new_cube['right'] = rotate_face_counterclockwise(new_cube['right'])
    new_cube['back'] = rotate_face_clockwise(rotate_face_clockwise(new_cube['back']))
    
    return new_cube

def color_to_face(color):
    """Convert color to Kociemba face notation"""
    return {
        'WHITE': 'U',
        'RED': 'R',
        'BLUE': 'F',
        'YELLOW': 'D',
        'ORANGE': 'L',
        'GREEN': 'B'
    }[color]

def get_face_string(face_data):
    """Convert a face to Kociemba string format"""
    result = []
    for i in range(3):
        for j in range(3):
            coord = f"{j},{i}"
            result.append(color_to_face(face_data[coord]))
    return ''.join(result)

def convert_to_kociemba(cube_data):
    """Convert cube data to Kociemba string"""
    # First transform the cube to match Kociemba orientation
    transformed = transform_cube(cube_data)
    
    # Then generate the string in URFDLB order
    faces = ['top', 'right', 'front', 'bottom', 'left', 'back']
    return ''.join(get_face_string(transformed[face]) for face in faces)

# Test with the provided cube state
cube_data = {
   "front": {
      "2,0": "BLUE",
      "1,0": "ORANGE",
      "0,0": "WHITE",
      "2,1": "YELLOW",
      "1,1": "RED",
      "0,1": "ORANGE",
      "2,2": "WHITE",
      "1,2": "WHITE",
      "0,2": "GREEN"
   },
   "back": {
      "2,2": "GREEN",
      "1,2": "RED",
      "0,2": "GREEN",
      "2,1": "ORANGE",
      "1,1": "ORANGE",
      "0,1": "YELLOW",
      "2,0": "RED",
      "1,0": "RED",
      "0,0": "RED"
   },
   "left": {
      "2,2": "YELLOW",
      "2,1": "YELLOW",
      "2,0": "YELLOW",
      "1,2": "BLUE",
      "1,1": "WHITE",
      "1,0": "GREEN",
      "0,2": "RED",
      "0,1": "WHITE",
      "0,0": "ORANGE"
   },
   "right": {
      "2,0": "YELLOW",
      "2,1": "BLUE",
      "2,2": "GREEN",
      "1,0": "GREEN",
      "1,1": "YELLOW",
      "1,2": "GREEN",
      "0,0": "WHITE",
      "0,1": "WHITE",
      "0,2": "YELLOW"
   },
   "top": {
      "2,0": "WHITE",
      "1,0": "RED",
      "0,0": "BLUE",
      "2,1": "ORANGE",
      "1,1": "BLUE",
      "0,1": "BLUE",
      "2,2": "BLUE",
      "1,2": "BLUE",
      "0,2": "RED"
   },
   "bottom": {
      "0,0": "ORANGE",
      "1,0": "RED",
      "2,0": "ORANGE",
      "0,1": "WHITE",
      "1,1": "GREEN",
      "2,1": "GREEN",
      "0,2": "BLUE",
      "1,2": "YELLOW",
      "2,2": "ORANGE"
   }
}

# Convert and print the Kociemba string
kociemba_string = convert_to_kociemba(cube_data)
print(kociemba_string)

solution = solve(kociemba_string)
print(f"Solution: {solution}")
