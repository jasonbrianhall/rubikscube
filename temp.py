    def set_solution_steps(self, solution_string):
        """Convert Kociemba solution string to rotation instructions"""
        self.solution_steps = []
        moves = solution_string.split()
        
        for move in moves:
            face = move[0]  # Get face letter (U, D, R, L, F, B)
            
            if len(move) > 1:
                if move[1] == '2':
                    angle = 180
                elif move[1] == "'":
                    angle = -90
                else:
                    angle = 90
            else:
                angle = 90

            print(f"Rotate {face_names[face]} face {direction_names[angle]}")
            
            # Map face to rotation parameters
            if face == 'U':
                self.solution_steps.append(('row', 1, angle))
            elif face == 'D':
                self.solution_steps.append(('row', -1, angle))
            elif face == 'R':
                self.solution_steps.append(('column', 1, angle))
            elif face == 'L':
                self.solution_steps.append(('column', -1, angle))
            elif face == 'F':
                self.solution_steps.append(('column', 0, angle))  # Front face uses middle column
            elif face == 'B':
                self.solution_steps.append(('column', 0, -angle))  # Back face is opposite direction
        
        self.current_step = -1
        self.is_solving = False
    
    def next_solution_step(self):
        """Execute next step in the solution"""
        if not self.is_solving or self.current_step >= len(self.solution_steps) - 1:
            return False
            
        self.current_step += 1
        move_type, pos, angle = self.solution_steps[self.current_step]
        
        if move_type == 'row':
            return self.start_row_rotation(angle / abs(angle), rotation_row=pos)
        elif move_type == 'column':
            return self.start_column_rotation(angle / abs(angle), rotation_column=pos)
        
        return True
        
