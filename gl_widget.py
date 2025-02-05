from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
from cube_model import RubiksCube

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cube = RubiksCube()
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)

    def keyPressEvent(self, event):
        if not self.cube.is_animating:
            if event.key() == Qt.Key_Left:
                self.start_rotation(1, -90)
            elif event.key() == Qt.Key_Right:
                self.start_rotation(1, 90)
            elif event.key() == Qt.Key_Up:
                self.start_rotation(0, -90)
            elif event.key() == Qt.Key_Down:
                self.start_rotation(0, 90)
            elif event.key() == Qt.Key_Q:  # Rotate top row counterclockwise
                if self.cube.start_row_rotation(-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_E:  # Rotate top row clockwise
                if self.cube.start_row_rotation(1):
                    self.animation_timer.start()                
            elif event.key() == Qt.Key_W:  # Rotate front column up
                if self.cube.start_column_rotation(-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_S:  # Rotate front column down
                if self.cube.start_column_rotation(1):
                    self.animation_timer.start()


    def start_rotation(self, axis, angle):
        if self.cube.animate_rotation(axis, angle):
            self.animation_timer.start()

    def update_animation(self):
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
