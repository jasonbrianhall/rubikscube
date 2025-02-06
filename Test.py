    def convert_cube_to_dict(self):
        """Convert the cube state to a dictionary mapping coordinates to colors for each face.
        Uses 0-based indexing where (0,0) is top-left and (2,2) is bottom-right for each face."""
        cube = self.gl_widget.cube
        cube_dict = {
            'front': {},
            'back': {},
            'left': {},
            'right': {},
            'top': {},
            'bottom': {}
        }
    
        # Face mappings adjusted to use 0-2 coordinate system
        face_mappings = {
            # Front face: standard view
            'front': {(x, y, 1): (2-y, x+1) for x in range(-1, 2) for y in range(-1, 2)},
            
            # Back face: viewed from behind
            'back': {(x, y, -1): (2-y, 3-x) for x in range(-1, 2) for y in range(-1, 2)},
            
            # Left face: when cube is rotated left
            'left': {(-1, y, z): (2-y, z+1) for y in range(-1, 2) for z in range(-1, 2)},
            
            # Right face: when cube is rotated right
            'right': {(1, y, z): (2-y, z+1) for y in range(-1, 2) for z in range(-1, 2)},
            
            # Top face: when looking down at cube
            'top': {(x, 1, z): (2-z, x+1) for x in range(-1, 2) for z in range(-1, 2)},
            
            # Bottom face: when looking up at cube
            'bottom': {(x, -1, z): (z, x+1) for x in range(-1, 2) for z in range(-1, 2)}
        }
    
        # Fill the dictionary with proper coordinate mapping
        for pos, cubelet in cube.cubelets.items():
            x, y, z = pos
            for face_name, mapping in face_mappings.items():
                if pos in mapping:
                    if face_name in cubelet['colors']:
                        row, col = mapping[pos]
                        # Adjust coordinates to be in 0-2 range
                        row = max(0, min(2, row))
                        col = max(0, min(2, col-1))
                        pos_key = f"{row},{col}"
                        cube_dict[face_name][pos_key] = cubelet['colors'][face_name].name
    
        # Sort the dictionary for each face
        for face in cube_dict:
            cube_dict[face] = dict(sorted(cube_dict[face].items()))
    
        print(json.dumps(cube_dict, indent=3))
        return cube_dict
    Last edited just now
