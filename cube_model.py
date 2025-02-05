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
                        ('top', [x, y, z]),
                        ('bottom', [x, y, z])
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
                           (face_type == 'top' and y == 1) or \
                           (face_type == 'bottom' and y == -1):
                            colors[face_type] = CubeColor.UNASSIGNED
                        else:
                            colors[face_type] = CubeColor.INTERIOR
                    
                    self.cubelets[key]['colors'] = colors

    def animate_rotation(self, axis, angle):
        """Start a rotation animation"""
        self.target_rotation[axis] = self.rotation[axis] + angle
        self.is_animating = True
        return self.is_animating

    def update_animation(self):
        """Update the rotation animation"""
        STEP_SIZE = 3  # Degrees per step
        still_animating = False

        for i in range(2):  # Only animate X and Y rotation (indices 0 and 1)
            if self.rotation[i] != self.target_rotation[i]:
                diff = self.target_rotation[i] - self.rotation[i]
                if abs(diff) <= STEP_SIZE:
                    self.rotation[i] = self.target_rotation[i]
                else:
                    self.rotation[i] += STEP_SIZE if diff > 0 else -STEP_SIZE
                    still_animating = True

        self.is_animating = still_animating
        return still_animating
        
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
        elif face_type == 'top':
            vertices = [[v[0], v[2], -v[1]] for v in vertices]
        elif face_type == 'bottom':
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

    def handle_click(self, click_x, click_y):
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
                print(f"Clicked cubelet at position {clicked_cubelet}, face {clicked_face_type}")
                self.cubelets[clicked_cubelet]['colors'][clicked_face_type] = self.selected_color
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
        self.face_coords = {}  # Reset face coordinates for this frame
        
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        
        for pos, cubelet in self.cubelets.items():
            glPushMatrix()
            x, y, z = pos
            glTranslatef(x, y, z)
            
            # Draw each face of the cubelet
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
        elif face_type == 'top':
            vertices = [[v[0], v[2], -v[1]] for v in vertices]
        elif face_type == 'bottom':
            vertices = [[v[0], -v[2], v[1]] for v in vertices]
        
        # Get screen coordinates for click detection
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
        
        # Draw black edges
        glColor3f(0, 0, 0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for v in vertices:
            glVertex3fv(v)
        glEnd()

    def get_cube_state(self):
        """Return the current state of the cube in a solver-friendly format"""
        state = {
            'top': [],
            'front': [],
            'right': [],
            'back': [],
            'left': [],
            'bottom': []
        }
        
        # Define the order for each face
        face_positions = {
            'top': [(x, 1, z) for z in [-1, 0, 1] for x in [-1, 0, 1]],
            'front': [(x, y, 1) for y in [1, 0, -1] for x in [-1, 0, 1]],
            'right': [(1, y, z) for y in [1, 0, -1] for z in [1, 0, -1]],
            'back': [(x, y, -1) for y in [1, 0, -1] for x in [1, 0, -1]],
            'left': [(-1, y, z) for y in [1, 0, -1] for z in [-1, 0, 1]],
            'bottom': [(x, -1, z) for z in [1, 0, -1] for x in [-1, 0, 1]]
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

    def set_solution_steps(self, solution):
        """Store solution steps and prepare for animation"""
        self.solution_steps = []
        for phase, moves in solution.items():
            for move in moves:
                face, direction = move.split('_')
                self.solution_steps.append((face, direction))
        self.current_step = -1
        self.is_solving = False
    
    def next_solution_step(self):
        """Execute next step in the solution"""
        if not self.is_solving or self.current_step >= len(self.solution_steps) - 1:
            return False
            
        self.current_step += 1
        face, direction = self.solution_steps[self.current_step]
        
        if direction == 'CW':
            self.rotate_face_clockwise(face)
        else:  # CCW
            self.rotate_face_counterclockwise(face)
        
        return True
    
    def previous_solution_step(self):
        """Undo the last solution step"""
        if not self.is_solving or self.current_step < 0:
            return False
            
        face, direction = self.solution_steps[self.current_step]
        
        # Apply opposite rotation
        if direction == 'CW':
            self.rotate_face_counterclockwise(face)
        else:  # CCW
            self.rotate_face_clockwise(face)
        
        self.current_step -= 1
        return True
    
    def start_solution_animation(self):
        """Start the solution animation"""
        self.is_solving = True
        self.current_step = -1
    
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
               (face_type == 'top' and y == 1) or \
               (face_type == 'bottom' and y == -1)
    
    def _update_face_visibility(self, pos):
        """Update which faces should be visible at a given position"""
        x, y, z = pos
        colors = self.cubelets[pos]['colors']
        
        # Check each face and set to interior if not exterior
        for face_type in colors:
            if not self._is_exterior_face(pos, face_type):
                colors[face_type] = CubeColor.INTERIOR
    
    def rotate_face_clockwise(self, face):
        """Rotate a face of the cube clockwise"""
        if face not in ['front', 'back', 'left', 'right', 'top', 'bottom']:
            print(f"Invalid face: {face}")
            return
    
        # Get affected cubelets and their current colors
        affected_cubelets = self._get_face_cubelets(face)
        old_state = {}
        
        # Store the entire state of affected cubelets
        for pos in affected_cubelets:
            if pos in self.cubelets:
                old_state[pos] = {
                    'colors': self.cubelets[pos]['colors'].copy(),
                    'faces': self.cubelets[pos]['faces'].copy()
                }
    
        # Define the rotation mappings for each face
        rotations = {
            'front': {
                (-1, 1, 1): (1, 1, 1),    # top-left → top-right
                (0, 1, 1): (1, 0, 1),     # top-middle → middle-right
                (1, 1, 1): (1, -1, 1),    # top-right → bottom-right
                (-1, 0, 1): (0, 1, 1),    # middle-left → top-middle
                (1, 0, 1): (0, -1, 1),    # middle-right → bottom-middle
                (-1, -1, 1): (-1, 1, 1),  # bottom-left → top-left
                (0, -1, 1): (-1, 0, 1),   # bottom-middle → middle-left
                (1, -1, 1): (-1, -1, 1)   # bottom-right → bottom-left
            },
            'back': {
                (-1, 1, -1): (1, 1, -1),
                (0, 1, -1): (1, 0, -1),
                (1, 1, -1): (1, -1, -1),
                (-1, 0, -1): (0, 1, -1),
                (1, 0, -1): (0, -1, -1),
                (-1, -1, -1): (-1, 1, -1),
                (0, -1, -1): (-1, 0, -1),
                (1, -1, -1): (-1, -1, -1)
            },
            'left': {
                (-1, 1, -1): (-1, 1, 1),
                (-1, 1, 0): (-1, 0, 1),
                (-1, 1, 1): (-1, -1, 1),
                (-1, 0, -1): (-1, 1, 0),
                (-1, 0, 1): (-1, -1, 0),
                (-1, -1, -1): (-1, 1, -1),
                (-1, -1, 0): (-1, 0, -1),
                (-1, -1, 1): (-1, -1, -1)
            },
            'right': {
                (1, 1, -1): (1, 1, 1),
                (1, 1, 0): (1, 0, 1),
                (1, 1, 1): (1, -1, 1),
                (1, 0, -1): (1, 1, 0),
                (1, 0, 1): (1, -1, 0),
                (1, -1, -1): (1, 1, -1),
                (1, -1, 0): (1, 0, -1),
                (1, -1, 1): (1, -1, -1)
            },
            'top': {
                (-1, 1, -1): (1, 1, -1),
                (0, 1, -1): (1, 1, 0),
                (1, 1, -1): (1, 1, 1),
                (-1, 1, 0): (0, 1, -1),
                (1, 1, 0): (0, 1, 1),
                (-1, 1, 1): (-1, 1, -1),
                (0, 1, 1): (-1, 1, 0),
                (1, 1, 1): (-1, 1, 1)
            },
            'bottom': {
                (-1, -1, -1): (1, -1, -1),
                (0, -1, -1): (1, -1, 0),
                (1, -1, -1): (1, -1, 1),
                (-1, -1, 0): (0, -1, -1),
                (1, -1, 0): (0, -1, 1),
                (-1, -1, 1): (-1, -1, -1),
                (0, -1, 1): (-1, -1, 0),
                (1, -1, 1): (-1, -1, 1)
            }
        }
    
        # Color rotation mappings for each face type
        color_rotations = {
            'front': {
                'top': 'right',
                'right': 'bottom',
                'bottom': 'left',
                'left': 'top'
            },
            'back': {
                'top': 'left',
                'left': 'bottom',
                'bottom': 'right',
                'right': 'top'
            },
            'left': {
                'top': 'front',
                'front': 'bottom',
                'bottom': 'back',
                'back': 'top'
            },
            'right': {
                'top': 'back',
                'back': 'bottom',
                'bottom': 'front',
                'front': 'top'
            },
            'top': {
                'front': 'right',
                'right': 'back',
                'back': 'left',
                'left': 'front'
            },
            'bottom': {
                'front': 'left',
                'left': 'back',
                'back': 'right',
                'right': 'front'
            }
        }
    
        # Apply the position rotations
        rotation_map = rotations[face]
        for old_pos, new_pos in rotation_map.items():
            if old_pos in old_state:
                # Copy colors from old position to new position
                new_colors = {}
                old_colors = old_state[old_pos]['colors']
                
                # First, set all faces to interior
                for face_type in old_colors:
                    new_colors[face_type] = CubeColor.INTERIOR
                
                # Then, copy only the exterior faces that should be visible
                for face_type, color in old_colors.items():
                    if color != CubeColor.INTERIOR and self._is_exterior_face(new_pos, face_type):
                        new_colors[face_type] = color
                
                # Apply the color rotation for the face being rotated
                rotated_colors = new_colors.copy()
                for old_face, new_face in color_rotations[face].items():
                    if old_face in new_colors and new_face in new_colors:
                        if self._is_exterior_face(new_pos, new_face):
                            rotated_colors[new_face] = new_colors[old_face]
                
                self.cubelets[new_pos]['colors'] = rotated_colors
                
                # Update visibility of all faces
                self._update_face_visibility(new_pos)
                
                
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
        elif face == 'top':
            for x in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((x, 1, z))
        elif face == 'bottom':
            for x in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    affected.append((x, -1, z))
        return affected                
