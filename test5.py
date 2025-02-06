def print_face_grid(face_str, face_name):
    """Print a 3x3 grid representation of a face"""
    print(f"\n{face_name} face:")
    print("-------------")
    for i in range(3):
        print("|", end=" ")
        for j in range(3):
            print(face_str[i*3 + j], end=" | ")
        print("\n-------------")

def print_kociemba_readable(kociemba_string):
    """Print a human-readable version of the Kociemba string"""
    print("\nKociemba String Visualization:")
    print("Each face is read from top-left to bottom-right")
    print("Face key: U=White, R=Blue, F=Red, D=Yellow, L=Green, B=Orange")
    
    # Print each face as a 3x3 grid
    faces = ['U', 'R', 'F', 'D', 'L', 'B']
    for i, face in enumerate(faces):
        start = i * 9
        face_str = kociemba_string[start:start + 9]
        print_face_grid(face_str, face)

def dict_to_kociemba_correct(cube):
    """
    Convert cube dictionary to Kociemba string format.
    Standard color scheme:
    - White on U (Up face)
    - Green on L (Left face)
    - Red on F (Front face)
    - Blue on R (Right face)
    - Orange on B (Back face)
    - Yellow on D (Down face)
    """
    # Color mapping to Kociemba notation
    color_map = {
        "WHITE": "U",   # Up face (should show as U)
        "YELLOW": "D",  # Down face (should show as D)
        "RED": "F",     # Front face (should show as F)
        "ORANGE": "B",  # Back face (should show as B)
        "GREEN": "L",   # Left face (should show as L)
        "BLUE": "R"     # Right face (should show as R)
    }
    
    # Kociemba requires faces in this order: U, R, F, D, L, B
    face_mapping = {
        'U': cube["top"],      # Up is top
        'R': cube["right"],    # Right is right
        'F': cube["front"],    # Front is front
        'D': cube["bottom"],   # Down is bottom
        'L': cube["left"],     # Left is left
        'B': cube["back"]      # Back is back
    }
    
    result = ""
    print("\nDebug - Face colors being read:")
    # Process faces in Kociemba order: U, R, F, D, L, B
    for face in ['U', 'R', 'F', 'D', 'L', 'B']:
        face_data = face_mapping[face]
        print(f"\n{face} face conversion:")
        # Read face from top-left to bottom-right
        for row in range(3):
            for col in range(3):
                coord = f"{row},{col}"
                color = face_data[coord]
                mapped = color_map[color]
                print(f"  Position ({row},{col}): {color} -> {mapped}")
                result += mapped
    
    return result

# Test with your cube data
test_cube = {
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

# Generate and print readable Kociemba string
kociemba_string = dict_to_kociemba_correct(test_cube)
print_kociemba_readable(kociemba_string)

print("\nComplete string:", kociemba_string)
print("Length:", len(kociemba_string))
