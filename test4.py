def dict_to_kociemba_corrected(cube):
    """
    Convert cube dictionary to Kociemba string format.
    Reads each face from left-to-right, top-to-bottom in Kociemba order
    """
    color_map = {
        "WHITE": "U",    # Up face
        "YELLOW": "D",   # Down face
        "RED": "F",      # Front face
        "ORANGE": "B",   # Back face
        "GREEN": "L",    # Left face
        "BLUE": "R"      # Right face
    }
    
    # Define face order for Kociemba
    face_order = ["top", "right", "front", "bottom", "left", "back"]
    
    result = ""
    # Process each face in Kociemba order
    for face_name in face_order:
        face = cube[face_name]
        # Read face in correct order: left-to-right, top-to-bottom
        for row in range(3):  # 0,1,2
            for col in range(3):  # 0,1,2
                coord = f"{row},{col}"  # This correctly maps to your coordinate system
                color = face[coord]
                result += color_map[color]
                
    return result

# Test with just the top face to verify
test_top = {
    "2,0": "WHITE",   # bottom-left
    "1,0": "RED",     # middle-left
    "0,0": "BLUE",    # top-left
    "2,1": "ORANGE",  # bottom-middle
    "1,1": "BLUE",    # center
    "0,1": "BLUE",    # top-middle
    "2,2": "BLUE",    # bottom-right
    "1,2": "BLUE",    # middle-right
    "0,2": "RED"      # top-right
}

# Let's print the values in the order we're reading them
print("Top face values in reading order:")
for row in range(3):
    for col in range(3):
        coord = f"{row},{col}"
        print(f"Position ({row},{col}): {test_top[coord]}")

# Test with your full cube
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
   "top": test_top,
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

kociemba_string = dict_to_kociemba_corrected(test_cube)
print("\nKociemba string by face:")
faces = ["U", "R", "F", "D", "L", "B"]
for i, face in enumerate(faces):
    start = i * 9
    face_str = kociemba_string[start:start + 9]
    print(f"{face} face: {face_str}")
