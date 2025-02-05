    def _complete_row_rotation(self):
        """Apply the rotation to the cube state after animation completes"""
        # Get all cubelets in the rotating row
        row_cubelets = {pos: data for pos, data in self.cubelets.items() if pos[1] == self.rotating_row_y}
        
        # Store old positions and their colors
        old_colors = {}
        for pos, data in row_cubelets.items():
            old_colors[pos] = data['colors'].copy()
        
        # Calculate new positions
        new_positions = {}
        for pos in row_cubelets:
            x, y, z = pos
            if self.row_rotation_direction > 0:  # Clockwise
                new_positions[pos] = (z, y, -x)
            else:  # Counter-clockwise
                new_positions[pos] = (-z, y, x)
        
        # Update cube state with new positions
        for old_pos, new_pos in new_positions.items():
            # Initialize new colors dict
            new_colors = {}
            for face_type in ['front', 'back', 'left', 'right', 'top', 'bottom']:
                new_colors[face_type] = CubeColor.INTERIOR
            
            # Map colors to new positions
            old_to_new_faces = {
                'front': 'right' if self.row_rotation_direction > 0 else 'left',
                'right': 'back' if self.row_rotation_direction > 0 else 'front',
                'back': 'left' if self.row_rotation_direction > 0 else 'right',
                'left': 'front' if self.row_rotation_direction > 0 else 'back',
                'top': 'top',
                'bottom': 'bottom'
            }
            
            for old_face, new_face in old_to_new_faces.items():
                if old_colors[old_pos][old_face] != CubeColor.INTERIOR:
                    new_colors[new_face] = old_colors[old_pos][old_face]
            
            # Update cubelet with new position and colors
            self.cubelets[new_pos] = {
                'pos': list(new_pos),
                'faces': self.cubelets[old_pos]['faces'],
                'colors': new_colors
            }
