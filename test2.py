from twophase import solve

def is_valid_kociemba(kociemba_string):
    if len(kociemba_string) != 54:
        return False, "Invalid length for Kociemba string."

    # Define the expected number of each piece type
    expected_edges = 12
    expected_corners = 8

    # Count occurrences of each color
    color_counts = {char: kociemba_string.count(char) for char in 'UDFLRB'}

    # Verify counts
    for color in color_counts:
        if color_counts[color] != 9:
            return False, f"Incorrect number of {color} stickers: {color_counts[color]} instead of 9."

    # Define edge and corner piece combinations
    edges = ['UF', 'UR', 'UB', 'UL', 'FR', 'FL', 'BR', 'BL', 'DF', 'DR', 'DB', 'DL']
    corners = ['UFR', 'UFL', 'UBL', 'UBR', 'DFL', 'DFR', 'DBR', 'DBL']

    # Count occurrences of each piece type
    edge_counts = {edge: kociemba_string.count(edge) for edge in edges}
    corner_counts = {corner: kociemba_string.count(corner) for corner in corners}

    # Check if there is exactly one of each edge and corner piece
    for edge in edge_counts:
        if edge_counts[edge] != 1:
            return False, f"Incorrect number of edge piece {edge}: {edge_counts[edge]} instead of 1."

    for corner in corner_counts:
        if corner_counts[corner] != 1:
            return False, f"Incorrect number of corner piece {corner}: {corner_counts[corner]} instead of 1."

    return True, "Kociemba string is valid."

def dict_to_kociemba(cube):
    # Define the color to character mapping
    color_map = {
        "WHITE": "U",
        "YELLOW": "D",
        "RED": "F",
        "ORANGE": "B",
        "GREEN": "L",
        "BLUE": "R"
    }
    
    # Function to get the kociemba string of a face
    def get_face_string(face):
        face_str = ""
        for i in range(3):
            for j in range(3):
                face_str += color_map[face[f"{2-j},{i}"]]
        return face_str

    # Map the provided cube structure to Kociemba string format
    kociemba_str = ""
    kociemba_str += get_face_string(cube["front"])
    kociemba_str += get_face_string(cube["right"])
    kociemba_str += get_face_string(cube["back"])
    kociemba_str += get_face_string(cube["left"])
    kociemba_str += get_face_string(cube["top"])
    kociemba_str += get_face_string(cube["bottom"])
    
    return kociemba_str
    
def visualize_cube(cube_dict):
    faces = ["top", "left", "front", "right", "back", "bottom"]
    for face in faces:
        print(f"{face.capitalize()} face:")
        for i in range(3):
            row = [cube_dict[face][f"{2-i},{j}"] for j in range(3)]
            print(" ".join(row))
        print



# Example cube dictionary
sample_data = {
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

'''kociemba_string = dict_to_kociemba(sample_data)
print(kociemba_string)

print(is_valid_kociemba(kociemba_string))

visualize_cube(sample_data)

#solution = solve(kociemba_string)
#print(f"Solution: {solution}")
'''

temp="DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD"
print(temp)
solution = solve(temp)
print(f"Solution: {solution}")

temp="URFRURFFFRRRDDDDDDRDRDFRUDRDDFDFRDRRDRRFRRDRRBFDFDBDBR"
print(temp)
solution = solve(temp)
print(f"Solution: {solution}")
