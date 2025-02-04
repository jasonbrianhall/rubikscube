import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cube = RubiksCube()
        self.setFocusPolicy(Qt.StrongFocus)  # Enable key events

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
        self.cubes = []
        self._initialize_cubes()

    def _initialize_cubes(self):
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    self.cubes.append((x, y, z))

    def draw(self):
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        
        for pos in self.cubes:
            x, y, z = pos
            glPushMatrix()
            glTranslatef(x, y, z)
            self.draw_cube()
            glPopMatrix()
    
    def draw_cube(self):
        vertices = [
            [0.4, 0.4, 0.4], [-0.4, 0.4, 0.4], [-0.4, -0.4, 0.4], [0.4, -0.4, 0.4],
            [0.4, 0.4, -0.4], [-0.4, 0.4, -0.4], [-0.4, -0.4, -0.4], [0.4, -0.4, -0.4]
        ]
        
        faces = [
            [0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7],
            [1, 5, 6, 2], [4, 5, 1, 0], [3, 2, 6, 7]
        ]
        
        glBegin(GL_QUADS)
        glColor3f(1, 1, 1)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        glColor3f(0, 0, 0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

class RubiksWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubiks Cube')
        self.setGeometry(100, 100, 1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget)
        
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        
        nav_layout = QHBoxLayout()
        self.up_btn = QPushButton('↑')
        self.down_btn = QPushButton('↓')
        self.left_btn = QPushButton('←')
        self.right_btn = QPushButton('→')
        
        # Connect button clicks to rotation methods
        self.up_btn.clicked.connect(lambda: self.rotate('up'))
        self.down_btn.clicked.connect(lambda: self.rotate('down'))
        self.left_btn.clicked.connect(lambda: self.rotate('left'))
        self.right_btn.clicked.connect(lambda: self.rotate('right'))
        
        for btn in [self.up_btn, self.down_btn, self.left_btn, self.right_btn]:
            btn.setFixedSize(60, 60)
            btn.setStyleSheet('font-size: 24px;')
        
        nav_layout.addWidget(self.left_btn)
        nav_layout.addWidget(self.right_btn)
        controls_layout.addWidget(self.up_btn, alignment=Qt.AlignHCenter)
        controls_layout.addLayout(nav_layout)
        controls_layout.addWidget(self.down_btn, alignment=Qt.AlignHCenter)
        
        colors = [
            ('Red', 'background-color: red'),
            ('Yellow', 'background-color: yellow'),
            ('Green', 'background-color: green'),
            ('Blue', 'background-color: blue'),
            ('Orange', 'background-color: orange'),
            ('White', 'background-color: white')
        ]
        
        for name, style in colors:
            btn = QPushButton()
            btn.setFixedSize(100, 100)
            btn.setStyleSheet(f'{style}; border: 2px solid black;')
            controls_layout.addWidget(btn)
        
        layout.addWidget(controls)

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
