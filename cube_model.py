from OpenGL.GL import *
from OpenGL.GLU import *
from colors import CubeColor

class RubiksCube:
    def __init__(self):
        self.rotation = [30, 45, 0]
        self.selected_color = CubeColor.RED
        self.cubelets = {}
        self.face_coords = {}
        self.target_rotation = [30, 45, 0]  # Target angles for animation
        self.is_animating = False
        self._initialize_cubes()
        self.rotating_row = False
        self.row_rotation_angle = 0
        self.target_row_angle = 0
        self.rotating_row_y = 1  # Top row y-coordinate
        self.row_rotation_direction = 1
        self.rotating_column = False
        self.column_rotation_angle = 0
        self.target_column_angle = 0
        self.rotating_col_x = 0
        self.rotating_face = False
        self.face_rotation_angle = 0
        self.target_face_angle = 0
        self.rotating_face_type = 'front'
        self.current_step = -1
        self.is_solving = False
        self.solution_steps = []

    def _initialize_cubes(self):
        """Initialize the 27 cubelets positions with interior faces"""
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    faces = []
                    # Add all six faces for every cubelet
                    faces.extend([
                        ('front', [x, y, z]),
                        ('back', [x, y, z]),
                        ('left', [x, y, z]),
                        ('right', [x, y, z]),
                        ('up', [x, y, z]),
                        ('down', [x, y, z])
                    ])
                    
                    key = (x, y, z)
                    self.cubelets[key] = {
                        'pos': [x, y, z],
                        'faces': faces,
                        'colors': {}
                    }
                    
                    # Set colors based on position
                    colors = {}
                    for face_type, _ in faces:
                        if (face_type == 'front' and z == 1) or \
                           (face_type == 'back' and z == -1) or \
                           (face_type == 'left' and x == -1) or \
                           (face_type == 'right' and x == 1) or \
                           (face_type == 'up' and y == 1) or \
                           (face_type == 'down' and y == -1):
                            colors[face_type] = CubeColor.UNASSIGNED
                        else:
                            colors[face_type] = CubeColor.INTERIOR
                    
                    self.cubelets[key]['colors'] = colors

    def start_row_rotation(self, direction, rotation_row=1):
        """Start rotating a row. Direction: 1 for clockwise, -1 for counterclockwise"""
        if not self.is_animating and not self.rotating_row:
            self.rotating_row = True
            self.row_rotation_angle = 0
            self.target_row_angle = 90 * direction
            self.row_rotation_direction = direction
            self.rotating_row_y = rotation_row
            return True
        return False

    def animate_rotation(self, axis, angle):
        """Start a rotation animation"""
        self.target_rotation[axis] = self.rotation[axis] + angle
        self.is_animating = True
        return self.is_animating

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
            for face_type in ['front', 'back', 'left', 'right', 'up', 'down']:
                new_colors[face_type] = CubeColor.INTERIOR
            
            # Map colors to new positions
            old_to_new_faces = {
                'front': 'right' if self.row_rotation_direction > 0 else 'left',
                'right': 'back' if self.row_rotation_direction > 0 else 'front',
                'back': 'left' if self.row_rotation_direction > 0 else 'right',
                'left': 'front' if self.row_rotation_direction > 0 else 'back',
                'up': 'up',
                'down': 'down'
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
        
    def _draw_cubelet_face(self, x, y, z, face_type, color):
        """Draw a single face of a cubelet"""
        vertices = [
            [-0.4, 0.4, 0.4], [-0.4, -0.4, 0.4], [0.4, -0.4, 0.4], [0.4, 0.4, 0.4]
        ]
        
        # Transform vertices based on face type
        if face_type == 'back':
            vertices = [[-v[0], v[1], -v[2]] for v in vertices]
        elif face_type == 'left':
            vertices = [[-v[2], v[1], v[0]] for v in vertices]
        elif face_type == 'right':
            vertices = [[v[2], v[1], -v[0]] for v in vertices]
        elif face_type == 'up':
            vertices = [[v[0], v[2], -v[1]] for v in vertices]
        elif face_type == 'down':
            vertices = [[v[0], -v[2], v[1]] for v in vertices]
        
        # Get screen coordinates for click detection
        if color != CubeColor.INTERIOR:  # Only track clickable faces
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)
            
            screen_coords = []
            for v in vertices:
                winX, winY, winZ = gluProject(v[0], v[1], v[2], modelview, projection, viewport)
                screen_x = int(round(winX) - viewport[0])
                screen_y = int(viewport[3] - round(winY) - viewport[1])
                screen_coords.append((screen_x, screen_y, winZ))
            
            # Store these coordinates for click detection
            key = (x, y, z)
            if key not in self.face_coords:
                self.face_coords[key] = {}
            self.face_coords[key][face_type] = screen_coords
        
        # Draw the colored face
        glBegin(GL_QUADS)
        glColor3f(*color.value)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
        
        # Draw black edges only for exterior faces
        if color != CubeColor.INTERIOR:
            glColor3f(0, 0, 0)
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            for v in vertices:
                glVertex3fv(v)
            glEnd()
            
    def set_selected_color(self, color: CubeColor):
        self.selected_color = color

    def handle_click(self, click_x, click_y, is_right_click=False):
        # Find the clicked face
        clicked_cubelet = None
        clicked_face_type = None
        closest_z = float('inf')
    
        for cubelet_pos, faces in self.face_coords.items():
            for face_type, coords in faces.items():
                if self._point_in_polygon(click_x, click_y, coords):
                    # Calculate average z-depth of face
                    avg_z = sum(z for _, _, z in coords) / len(coords)
                    if avg_z < closest_z:
                        closest_z = avg_z
                        clicked_cubelet = cubelet_pos
                        clicked_face_type = face_type
    
        if clicked_cubelet and clicked_face_type:
            # Don't change the color if it's an interior face
            current_color = self.cubelets[clicked_cubelet]['colors'][clicked_face_type]
            if current_color != CubeColor.INTERIOR:
                self.cubelets[clicked_cubelet]['colors'][clicked_face_type] = CubeColor.UNASSIGNED if is_right_click else self.selected_color
                return True
        return False
        
    def _point_in_polygon(self, x, y, vertices):
        """Ray casting algorithm to determine if point is inside polygon"""
        n = len(vertices)
        inside = False
        
        j = n - 1
        for i in range(n):
            if ((vertices[i][1] > y) != (vertices[j][1] > y) and
                x < (vertices[j][0] - vertices[i][0]) * (y - vertices[i][1]) /
                    (vertices[j][1] - vertices[i][1]) + vertices[i][0]):
                inside = not inside
            j = i
        
        return inside

    def draw(self):
        self.face_coords = {}
    
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
    
        for pos, cubelet in self.cubelets.items():
            glPushMatrix()
            x, y, z = pos
        
            if self.rotating_row and y == self.rotating_row_y:
                glTranslatef(0, y, 0)
                glRotatef(self.row_rotation_angle, 0, 1, 0)
                glTranslatef(x, 0, z)
            elif self.rotating_column and x == self.rotating_col_x:
                glTranslatef(x, 0, 0)
                glRotatef(self.column_rotation_angle, 1, 0, 0)
                glTranslatef(0, y, z)
            else:
                glTranslatef(x, y, z)
        
            for face_type, _ in cubelet['faces']:
                self._draw_cubelet_face(x, y, z, face_type, cubelet['colors'][face_type])
        
            glPopMatrix()
            
    def _draw_cubelet_face(self, x, y, z, face_type, color):
        """Draw a single face of a cubelet"""
        vertices = [
            [-0.4, 0.4, 0.4], [-0.4, -0.4, 0.4], [0.4, -0.4, 0.4], [0.4, 0.4, 0.4]
        ]
    
        # Transform vertices based on face type
        if face_type == 'back':
            vertices = [[-v[0], v[1], -v[2]] for v in vertices]
        elif face_type == 'left':
            vertices = [[-v[2], v[1], v[0]] for v in vertices]
        elif face_type == 'right':
            vertices = [[v[2], v[1], -v[0]] for v in vertices]
        elif face_type == 'up':
            vertices = [[v[0], v[2], -v[1]] for v in vertices]
        elif face_type == 'down':
            vertices = [[v[0], -v[2], v[1]] for v in vertices]
    
        # Get screen coordinates for click detection
        if color != CubeColor.INTERIOR:  # Only track clickable faces
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)
        
            screen_coords = []
            for v in vertices:
                winX, winY, winZ = gluProject(v[0], v[1], v[2], modelview, projection, viewport)
                screen_x = int(round(winX) - viewport[0])
                screen_y = int(viewport[3] - round(winY) - viewport[1])
                screen_coords.append((screen_x, screen_y, winZ))
        
            # Store these coordinates for click detection
            key = (x, y, z)
            if key not in self.face_coords:
                self.face_coords[key] = {}
            self.face_coords[key][face_type] = screen_coords
    
        # Draw the colored face
        glBegin(GL_QUADS)
        glColor3f(*color.value)
        for v in vertices:
            glVertex3fv(v)
        glEnd()
    
        # Draw black edges only for exterior faces
        if color != CubeColor.INTERIOR:
            glColor3f(0, 0, 0)
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            for v in vertices:
                glVertex3fv(v)
            glEnd()

    def get_cube_state(self):
        """Return the current state of the cube in a solver-friendly format"""
        state = {
            'up': [],
            'front': [],
            'right': [],
            'back': [],
            'left': [],
            'down': []
        }
        
        # Define the order for each face
        face_positions = {
            'up': [(x, 1, z) for z in [-1, 0, 1] for x in [-1, 0, 1]],
            'front': [(x, y, 1) for y in [1, 0, -1] for x in [-1, 0, 1]],
            'right': [(1, y, z) for y in [1, 0, -1] for z in [1, 0, -1]],
            'back': [(x, y, -1) for y in [1, 0, -1] for x in [1, 0, -1]],
            'left': [(-1, y, z) for y in [1, 0, -1] for z in [-1, 0, 1]],
            'down': [(x, -1, z) for z in [1, 0, -1] for x in [-1, 0, 1]]
        }
        
        # Fill in the state
        for face_name, positions in face_positions.items():
            for pos in positions:
                if pos in self.cubelets and face_name in self.cubelets[pos]['colors']:
                    color = self.cubelets[pos]['colors'][face_name]
                    state[face_name].append(color)
                else:
                    state[face_name].append(CubeColor.UNASSIGNED)
        
        return state

    def next_solution_step(self):
        if not self.is_solving or self.current_step >= len(self.solution_steps) - 1:
            print("No more steps or not solving")
            return False
    
        self.current_step += 1
        move_type, pos, angle = self.solution_steps[self.current_step]
        print(f"\nExecuting step {self.current_step + 1}/{len(self.solution_steps)}: {move_type}, position {pos}, angle {angle}")

        if abs(angle) == 180:
            direction = angle / abs(angle)
            self.solution_steps.insert(self.current_step + 1, (move_type, pos, 90 * direction))
            if move_type == 'row':
                return self.start_row_rotation(direction, rotation_row=pos)
            elif move_type == 'column':
                return self.start_column_rotation(direction, rotation_column=pos)
            elif move_type == 'face':
                return self.start_face_rotation(direction, face=pos)

        if move_type == 'row':
            return self.start_row_rotation(angle / abs(angle), rotation_row=pos)
        elif move_type == 'column':
            return self.start_column_rotation(angle / abs(angle), rotation_column=pos)
        elif move_type == 'face':
            return self.start_face_rotation(angle / abs(angle), face=pos)

        print("Unknown move type")
        return False
            
    def execute_double_rotation(self, move_type, pos, angle):
        """Handle 180-degree rotations by breaking into two 90-degree steps"""
        if abs(angle) == 180:
            direction = angle / abs(angle)
            # Queue up both 90-degree rotations at once
            if isinstance(pos, list):  # For front/back face moves
                for x in pos:
                    self.solution_steps.insert(self.current_step + 1, (move_type, x, 90 * direction))
                    self.solution_steps.insert(self.current_step + 2, (move_type, x, 90 * direction))
            else:
                self.solution_steps.insert(self.current_step + 1, (move_type, pos, 90 * direction))
                self.solution_steps.insert(self.current_step + 2, (move_type, pos, 90 * direction))
            return True
        return False

    def set_solution_steps(self, solution_string):
        """Convert Kociemba solution string to rotation instructions"""
        self.solution_steps = []
        moves = solution_string.split()
    
        face_names = {
            'U': 'Top', 'D': 'Bottom', 'R': 'Right',
        'L': 'Left', 'F': 'Front', 'B': 'Back'
        }
        direction_names = {
            90: 'clockwise', -90: 'counter-clockwise', 180: 'twice'
        }
    
        print("\nSolution steps:")
        for move in moves:
            face = move[0]
            angle = 180 if len(move) > 1 and move[1] == '2' else \
                   90 if len(move) > 1 and move[1] == "'" else -90
            
            print(f"Rotate {face_names[face]} face {direction_names[angle]}")
        
            # Map face to rotation parameters
            if face == 'U':
                self.solution_steps.append(('row', 1, angle))
            elif face == 'D':
                self.solution_steps.append(('row', -1, -angle))
            elif face == 'R':
                self.solution_steps.append(('column', 1, angle))
            elif face == 'L':
                self.solution_steps.append(('column', -1, -angle))
            elif face == 'F':
                self.solution_steps.append(('face', 'front', angle))
            elif face == 'B':
                self.solution_steps.append(('face', 'back', angle))    
        self.current_step = -1
        self.is_solving = False
        
    def previous_solution_step(self):
        """Undo last solution step"""
        if self.current_step < 0:
            return False
        
        move_type, index, angle = self.solution_steps[self.current_step]
        # Reverse the angle for undoing
        angle = -angle
    
        if move_type == 'row':
            self.start_row_rotation(angle / abs(angle), rotation_row=index)
        elif move_type == 'column':
            self.start_column_rotation(angle / abs(angle), rotation_column=index)
        elif move_type == 'face':
            self.start_face_rotation(angle / abs(angle), face=index)  # Changed from rotation_face to face
    
        self.current_step -= 1
        return True    

    def start_solution_animation(self):
        """Start the solution animation"""
        self.is_solving = True
        self.current_step = -1

    def start_column_rotation(self, direction, rotation_column=1):
        """Start rotating a column"""
        print(f"Attempting column rotation with direction {direction}, column {rotation_column}")
        if not self.is_animating and not self.rotating_column:
            print("Animation starting - setting rotation parameters")
            self.rotating_column = True
            self.column_rotation_angle = 0
            self.target_column_angle = 90 * direction
            self.column_rotation_direction = direction
            self.rotating_col_x = rotation_column
            return True
        print("Animation blocked - already animating or rotating")
        return False
    
    def reset_solution(self):
        """Reset the solution animation to the beginning"""
        while self.current_step >= 0:
            self.previous_solution_step()
        self.is_solving = False
        
    def _is_exterior_face(self, pos, face_type):
        """Determine if a face is on the exterior of the cube"""
        x, y, z = pos
        return (face_type == 'front' and z == 1) or \
               (face_type == 'back' and z == -1) or \
               (face_type == 'left' and x == -1) or \
               (face_type == 'right' and x == 1) or \
               (face_type == 'up' and y == 1) or \
               (face_type == 'down' and y == -1)
    
    def _update_face_visibility(self, pos):
        """Update which faces should be visible at a given position"""
        x, y, z = pos
        colors = self.cubelets[pos]['colors']
        
        # Check each face and set to interior if not exterior
        for face_type in colors:
            if not self._is_exterior_face(pos, face_type):
                colors[face_type] = CubeColor.INTERIOR
    
    def rotate_face_clockwise(self, face):
        """Initiate face rotation animation"""
        if face not in ['front', 'back', 'left', 'right', 'up', 'down']:
            print(f"Invalid face: {face}")
            return
        
        if not self.is_animating and not self.rotating_face:
            self.rotating_face = True
            self.face_rotation_angle = 0
            self.target_face_angle = 90
            self.face_rotation_direction = 1
            self.rotating_face_type = face
            return True
        return False    

                
                
    def _get_face_cubelets(self, face):
        """Get the cubelets that form a face"""
        affected = []
        if face == 'front':
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    affected.append((x, y, 1))
        elif face == 'back':
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    affected.append((x, y, -1))
        elif face == 'left':
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((-1, y, z))
        elif face == 'right':
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((1, y, z))
        elif face == 'up':
            for x in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((x, 1, z))
        elif face == 'down':
            for x in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((x, -1, z))
        return affected                
        
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
            for face_type in ['front', 'back', 'left', 'right', 'up', 'down']:
                new_x, new_y, new_z = new_pos
                if ((face_type == 'front' and new_z == 1) or 
                    (face_type == 'back' and new_z == -1) or
                    (face_type == 'left' and new_x == -1) or
                    (face_type == 'right' and new_x == 1) or
                    (face_type == 'up' and new_y == 1) or
                    (face_type == 'down' and new_y == -1)):
                    
                    # Map colors based on rotation direction
                    if face_type == 'left' or face_type == 'right':
                        new_colors[face_type] = exterior_faces[old_pos].get(face_type, CubeColor.UNASSIGNED)
                    else:
                        if self.column_rotation_direction > 0:  # Down
                            if face_type == 'front': new_colors[face_type] = exterior_faces[old_pos].get('up', CubeColor.UNASSIGNED)
                            elif face_type == 'up': new_colors[face_type] = exterior_faces[old_pos].get('back', CubeColor.UNASSIGNED)
                            elif face_type == 'back': new_colors[face_type] = exterior_faces[old_pos].get('down', CubeColor.UNASSIGNED)
                            elif face_type == 'down': new_colors[face_type] = exterior_faces[old_pos].get('front', CubeColor.UNASSIGNED)
                        else:  # Up
                            if face_type == 'front': new_colors[face_type] = exterior_faces[old_pos].get('down', CubeColor.UNASSIGNED)
                            elif face_type == 'up': new_colors[face_type] = exterior_faces[old_pos].get('front', CubeColor.UNASSIGNED)
                            elif face_type == 'back': new_colors[face_type] = exterior_faces[old_pos].get('up', CubeColor.UNASSIGNED)
                            elif face_type == 'down': new_colors[face_type] = exterior_faces[old_pos].get('back', CubeColor.UNASSIGNED)
                else:
                    new_colors[face_type] = CubeColor.INTERIOR
    
            # Update cubelet
            self.cubelets[new_pos] = {
                'pos': list(new_pos),
                'faces': self.cubelets[old_pos]['faces'],
                'colors': new_colors
            }
            
    def start_face_rotation(self, direction, face='front'):
        """Start rotating a face. direction: 1 for clockwise, -1 for counterclockwise"""
        if not self.is_animating and not self.rotating_face:
            self.rotating_face = True
            self.face_rotation_angle = 0
            self.target_face_angle = 90 * direction
            self.face_rotation_direction = direction
            self.rotating_face_type = face
            return True
        return False
    
    def draw(self):
        self.face_coords = {}
    
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
    
        for pos, cubelet in self.cubelets.items():
            glPushMatrix()
            x, y, z = pos
    
            if self.rotating_row and y == self.rotating_row_y:
                glTranslatef(0, y, 0)
                glRotatef(self.row_rotation_angle, 0, 1, 0)
                glTranslatef(x, 0, z)
            elif self.rotating_column and x == self.rotating_col_x:
                glTranslatef(x, 0, 0)
                glRotatef(self.column_rotation_angle, 1, 0, 0)
                glTranslatef(0, y, z)
            elif self.rotating_face:
                if (self.rotating_face_type == 'front' and z == 1) or \
                   (self.rotating_face_type == 'back' and z == -1):
                    if self.rotating_face_type == 'front':
                        glTranslatef(0, 0, 1)
                        glRotatef(self.face_rotation_angle, 0, 0, 1)
                        glTranslatef(x, y, 0)
                    else:  # back
                        glTranslatef(0, 0, -1)
                        glRotatef(self.face_rotation_angle, 0, 0, -1)
                        glTranslatef(x, y, 0)
                else:
                    glTranslatef(x, y, z)
            else:
                glTranslatef(x, y, z)
    
            for face_type, _ in cubelet['faces']:
                self._draw_cubelet_face(x, y, z, face_type, cubelet['colors'][face_type])
    
            glPopMatrix()
    
    def update_animation(self):
        """Update animation state"""
        STEP_SIZE = 3
        still_animating = False
        if self.rotating_row:
            diff = self.target_row_angle - self.row_rotation_angle
            if abs(diff) <= STEP_SIZE:
                self.row_rotation_angle = self.target_row_angle
                self.rotating_row = False
                self._complete_row_rotation()
            else:
                self.row_rotation_angle += STEP_SIZE if diff > 0 else -STEP_SIZE
                still_animating = True
        elif self.rotating_column:
            diff = self.target_column_angle - self.column_rotation_angle
            if abs(diff) <= STEP_SIZE:
                self.column_rotation_angle = self.target_column_angle
                self.rotating_column = False
                self._complete_column_rotation()
            else:
                self.column_rotation_angle += STEP_SIZE if diff > 0 else -STEP_SIZE
                still_animating = True
        elif self.rotating_face:
            diff = self.target_face_angle - self.face_rotation_angle
            if abs(diff) <= STEP_SIZE:
                self.face_rotation_angle = self.target_face_angle
                self.rotating_face = False
                self._complete_face_rotation()
            else:
                self.face_rotation_angle += STEP_SIZE if diff > 0 else -STEP_SIZE
                still_animating = True
        else:
            for i in range(2):
                if self.rotation[i] != self.target_rotation[i]:
                    diff = self.target_rotation[i] - self.rotation[i]
                    if abs(diff) <= STEP_SIZE:
                        self.rotation[i] = self.target_rotation[i]
                    else:
                        self.rotation[i] += STEP_SIZE if diff > 0 else -STEP_SIZE
                        still_animating = True
    
        self.is_animating = still_animating or self.rotating_row or self.rotating_column or self.rotating_face
        return self.is_animating      
        
    def _complete_face_rotation(self):
        """Apply the rotation to the cube state after face animation completes"""
        print(f"\nCompleting {self.rotating_face_type} face rotation")
        print(f"Direction: {'clockwise' if self.face_rotation_direction > 0 else 'counter-clockwise'}")
    
        # Get affected cubelets
        face_cubelets = self._get_face_cubelets(self.rotating_face_type)
    
        # Store old positions and their colors
        old_colors = {}
        for pos in face_cubelets:
            if pos in self.cubelets:
                old_colors[pos] = self.cubelets[pos]['colors'].copy()
    
        # Calculate new positions based on 90-degree rotation
        new_positions = {}
        for pos in face_cubelets:
            x, y, z = pos
            if self.rotating_face_type == 'front':
                new_positions[pos] = (-y, x, z) if self.face_rotation_direction > 0 else (y, -x, z)
            elif self.rotating_face_type == 'back':
                new_positions[pos] = (y, -x, z) if self.face_rotation_direction > 0 else (-y, x, z)
    
        # Update cube state with new positions
        for old_pos, new_pos in new_positions.items():
            # Map colors based on the rotation
            new_colors = {}
            for face_type in ['front', 'back', 'left', 'right', 'up', 'down']:
                new_colors[face_type] = CubeColor.INTERIOR  # Default to interior
            
            # Map the face colors based on rotation direction
            if self.rotating_face_type == 'front':
                # For front face, when rotating clockwise:
                # - Colors on right face move to down
                # - Colors on up face move to right
                # - Colors on left face move to up
                # - Colors on down face move to left
                old_to_new_faces = {
                    'front': 'front',  # Front face colors stay on front
                    'right': 'up' if self.face_rotation_direction > 0 else 'down',
                    'up': 'left' if self.face_rotation_direction > 0 else 'right',
                    'left': 'down' if self.face_rotation_direction > 0 else 'up',
                    'down': 'right' if self.face_rotation_direction > 0 else 'left'
                }
            elif self.rotating_face_type == 'back':
                # For back face, when rotating clockwise:
                # - Colors on right face move to up
                # - Colors on up face move to left
                # - Colors on left face move to down
                # - Colors on down face move to right
                old_to_new_faces = {
                    'back': 'back',  # Back face colors stay on back
                    'right': 'down' if self.face_rotation_direction > 0 else 'up',
                    'up': 'right' if self.face_rotation_direction > 0 else 'left',
                    'left': 'up' if self.face_rotation_direction > 0 else 'down',
                    'down': 'left' if self.face_rotation_direction > 0 else 'right'
                }
            
            # Apply the color mapping
            for old_face, new_face in old_to_new_faces.items():
                if old_colors[old_pos][old_face] != CubeColor.INTERIOR:
                    new_colors[new_face] = old_colors[old_pos][old_face]
        
            # Update cubelet with new position and colors
            self.cubelets[new_pos] = {
                'pos': list(new_pos),
                'faces': self.cubelets[old_pos]['faces'],
                'colors': new_colors
            }
    
        return True
