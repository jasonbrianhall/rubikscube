    def _complete_column_rotation(self):
        """Apply the rotation to the cube state after column animation completes"""
        column_cubelets = {pos: data for pos, data in self.cubelets.items() if pos[0] == self.rotating_col_x}
        
        # First pass: store all exterior face colors
        exterior_faces = {}
        for pos, data in column_cubelets.items():
            x, y, z = pos
            exterior_faces[pos] = {}
            for face_type, color in data['colors'].items():
                if color != CubeColor.INTERIOR:
                    exterior_faces[pos][face_type] = color
    
        # Calculate new positions and update the cube
        new_positions = {}
        for pos in column_cubelets:
            x, y, z = pos
            if self.column_rotation_direction > 0:  # Down
                new_positions[pos] = (x, -z, y)
            else:  # Up
                new_positions[pos] = (x, z, -y)
    
        # Update cube state with new positions and rotated colors
        for old_pos, new_pos in new_positions.items():
            new_colors = {}
            # Initialize all faces as interior
            for face_type in ['front', 'back', 'left', 'right', 'top', 'bottom']:
                new_x, new_y, new_z = new_pos
                if ((face_type == 'front' and new_z == 1) or 
                    (face_type == 'back' and new_z == -1) or
                    (face_type == 'left' and new_x == -1) or
                    (face_type == 'right' and new_x == 1) or
                    (face_type == 'top' and new_y == 1) or
                    (face_type == 'bottom' and new_y == -1)):
                    
                    # Map colors based on rotation direction
                    if face_type == 'left' or face_type == 'right':
                        new_colors[face_type] = exterior_faces[old_pos].get(face_type, CubeColor.UNASSIGNED)
                    else:
                        if self.column_rotation_direction > 0:  # Down
                            if face_type == 'front': new_colors[face_type] = exterior_faces[old_pos].get('top', CubeColor.UNASSIGNED)
                            elif face_type == 'top': new_colors[face_type] = exterior_faces[old_pos].get('back', CubeColor.UNASSIGNED)
                            elif face_type == 'back': new_colors[face_type] = exterior_faces[old_pos].get('bottom', CubeColor.UNASSIGNED)
                            elif face_type == 'bottom': new_colors[face_type] = exterior_faces[old_pos].get('front', CubeColor.UNASSIGNED)
                        else:  # Up
                            if face_type == 'front': new_colors[face_type] = exterior_faces[old_pos].get('bottom', CubeColor.UNASSIGNED)
                            elif face_type == 'top': new_colors[face_type] = exterior_faces[old_pos].get('front', CubeColor.UNASSIGNED)
                            elif face_type == 'back': new_colors[face_type] = exterior_faces[old_pos].get('top', CubeColor.UNASSIGNED)
                            elif face_type == 'bottom': new_colors[face_type] = exterior_faces[old_pos].get('back', CubeColor.UNASSIGNED)
                else:
                    new_colors[face_type] = CubeColor.INTERIOR
    
            # Update cubelet
            self.cubelets[new_pos] = {
                'pos': list(new_pos),
                'faces': self.cubelets[old_pos]['faces'],
                'colors': new_colors
            }
