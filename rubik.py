import sys
from enum import Enum
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QOpenGLWidget, QMenuBar, QMenu, QAction
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class CubeColor(Enum):
    RED = (1.0, 0.0, 0.0)
    YELLOW = (1.0, 1.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    ORANGE = (1.0, 0.5, 0.0)
    WHITE = (1.0, 1.0, 1.0)
    UNASSIGNED = (0.8, 0.8, 0.8)

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cube = RubiksCube()
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.cube.rotation[1] -= 90
        elif event.key() == Qt.Key_Right:
            self.cube.rotation[1] += 90
        elif event.key() == Qt.Key_Up:
            self.cube.rotation[0] -= 90
        elif event.key() == Qt.Key_Down:
            self.cube.rotation[0] += 90
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
        self._initialize_cubes()

    def _initialize_cubes(self):
        """Initialize the 27 cubelets positions"""
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    # Only add faces for outer cubelets
                    faces = []
                    # Front/Back faces (z)
                    if z == 1:  # Front
                        faces.append(('front', [x, y, z]))
                    elif z == -1:  # Back
                        faces.append(('back', [x, y, z]))
                    # Left/Right faces (x)
                    if x == -1:  # Left
                        faces.append(('left', [x, y, z]))
                    elif x == 1:  # Right
                        faces.append(('right', [x, y, z]))
                    # Top/Bottom faces (y)
                    if y == 1:  # Top
                        faces.append(('top', [x, y, z]))
                    elif y == -1:  # Bottom
                        faces.append(('bottom', [x, y, z]))
                        
                    if faces:  # Only add cubelets with visible faces
                        key = (x, y, z)
                        self.cubelets[key] = {
                            'pos': [x, y, z],
                            'faces': faces,
                            'colors': {face[0]: CubeColor.UNASSIGNED for face in faces}
                        }

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
        
        # Add menu actions
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_state)
        file_menu.addAction(save_action)
        
        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.clear_cube)
        file_menu.addAction(clear_action)
        
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
        if direction == 'up':
            self.gl_widget.cube.rotation[0] -= 90
        elif direction == 'down':
            self.gl_widget.cube.rotation[0] += 90
        elif direction == 'left':
            self.gl_widget.cube.rotation[1] -= 90
        elif direction == 'right':
            self.gl_widget.cube.rotation[1] += 90
        self.gl_widget.update()

def main():
    app = QApplication(sys.argv)
    window = RubiksWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
