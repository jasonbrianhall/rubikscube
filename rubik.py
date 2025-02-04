import sys
from enum import Enum
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QOpenGLWidget, QMenuBar, QMenu, QAction
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PyQt5.QtCore import QTimer


class CubeColor(Enum):
    RED = (1.0, 0.0, 0.0)
    YELLOW = (1.0, 1.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    ORANGE = (1.0, 0.5, 0.0)
    WHITE = (1.0, 1.0, 1.0)
    UNASSIGNED = (0.8, 0.8, 0.8)
    INTERIOR = (0, 0, 0)  # New dark gray color for interior faces

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cube = RubiksCube()
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Setup animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)  # ~60 FPS

    def keyPressEvent(self, event):
        if not self.cube.is_animating:  # Only start new rotation if not already animating
            if event.key() == Qt.Key_Left:
                self.start_rotation(1, -90)
            elif event.key() == Qt.Key_Right:
                self.start_rotation(1, 90)
            elif event.key() == Qt.Key_Up:
                self.start_rotation(0, -90)
            elif event.key() == Qt.Key_Down:
                self.start_rotation(0, 90)

    def start_rotation(self, axis, angle):
        """Start a rotation animation"""
        if self.cube.animate_rotation(axis, angle):
            self.animation_timer.start()

    def update_animation(self):
        """Update the animation state"""
        if not self.cube.update_animation():
            self.animation_timer.stop()
        self.update()

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        if self.cube.handle_click(x, y):
            self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.9, 0.9, 0.9, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 50.0)
        glTranslatef(0.0, 0.0, -15)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.cube.draw()

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

class RubiksWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubiks Cube State Input')
        self.setGeometry(100, 100, 800, 600)
        
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        view_menu = menubar.addMenu('View')  # Add new View menu
        
        # Add menu actions
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_state)
        file_menu.addAction(save_action)
        
        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.clear_cube)
        file_menu.addAction(clear_action)

        debug_action = QAction('Debug Cube State', self)
        debug_action.triggered.connect(self.print_cube_state)
        view_menu.addAction(debug_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_action)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create top control bar
        controls = QWidget()
        controls.setMaximumHeight(40)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(2)
        controls_layout.setContentsMargins(5, 0, 5, 0)
        
        # Navigation buttons
        nav_buttons = {'←': 'left', '↑': 'up', '↓': 'down', '→': 'right'}
        for text, direction in nav_buttons.items():
            btn = QPushButton(text)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet('font-size: 14px;')
            btn.clicked.connect(lambda checked, d=direction: self.rotate(d))
            controls_layout.addWidget(btn)
        
        controls_layout.addSpacing(20)  # Add space between navigation and colors
        
        # Color buttons
        colors = [
            ('Red', 'red', CubeColor.RED),
            ('Yellow', 'yellow', CubeColor.YELLOW),
            ('Green', 'green', CubeColor.GREEN),
            ('Blue', 'blue', CubeColor.BLUE),
            ('Orange', 'orange', CubeColor.ORANGE),
            ('White', 'white', CubeColor.WHITE)
        ]
        
        for name, color, enum in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f'background-color: {color}; border: 2px solid black;')
            btn.clicked.connect(lambda checked, c=enum: self.set_color(c))
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()  # Push everything to the left
        layout.addWidget(controls)
        
        # Add GL widget
        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget)

    def print_cube_state(self):
        """Print the current state of all cubelet positions and their colors"""
        cube = self.gl_widget.cube
        
        print("\n=== CUBE STATE DUMP ===")
    
        # Sort positions for consistent output
        positions = sorted(cube.cubelets.keys())
    
        for pos in positions:
            cubelet = cube.cubelets[pos]
            x, y, z = pos
        
            print(f"\nPosition ({x}, {y}, {z}):")
            for face, color in cubelet['colors'].items():
                if color != CubeColor.INTERIOR:  # Only show visible faces
                    print(f"  {face:6} face: {color.name:8}")

    def save_state(self):
        state = self.gl_widget.cube.get_cube_state()
        print("Saving cube state:")
        for face_name, colors in state.items():
            print(f"{face_name}: {[c.name for c in colors]}")
    
    def clear_cube(self):
        print("Clearing cube")
        self.gl_widget.cube = RubiksCube()
        self.gl_widget.update()
    
    def set_color(self, color: CubeColor):
        self.gl_widget.cube.set_selected_color(color)

    def rotate(self, direction):
        if not self.gl_widget.cube.is_animating:  # Only start new rotation if not already animating
            if direction == 'up':
                self.gl_widget.start_rotation(0, -90)
            elif direction == 'down':
                self.gl_widget.start_rotation(0, 90)
            elif direction == 'left':
                self.gl_widget.start_rotation(1, -90)
            elif direction == 'right':
                self.gl_widget.start_rotation(1, 90)

def main():
    app = QApplication(sys.argv)
    window = RubiksWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
