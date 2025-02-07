from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from cube_model import RubiksCube
from colors import CubeColor
import time

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cube = RubiksCube()
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)
        
        # Mouse tracking variables
        self.last_pos = QPoint()
        self.mouse_pressed = False
        self.right_mouse_pressed = False

        self.zoom_level = -15
        self.setMouseTracking(True)

    def next_step(self):
        """Execute next solution step"""
        print("GLWidget: Next step pressed")
        if self.cube.next_solution_step():
            print("GLWidget: Starting animation timer")
            self.animation_timer.start()
            self.update()
        else:
            print("GLWidget: No step to animate")

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
            elif event.key() == Qt.Key_A:  # Rotate top row counterclockwise
                if self.cube.start_row_rotation(-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_D:  # Rotate top row clockwise
                if self.cube.start_row_rotation(1):
                    self.animation_timer.start()                
            elif event.key() == Qt.Key_W:  # Rotate front column up
                if self.cube.start_column_rotation(-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_S:  # Rotate front column down
                if self.cube.start_column_rotation(1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_H:  # Rotate top row counterclockwise
                if self.cube.start_row_rotation(-1, rotation_row=-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_F:  # Rotate top row clockwise
                if self.cube.start_row_rotation(1, rotation_row=-1):
                    self.animation_timer.start()                
            elif event.key() == Qt.Key_T:  # Rotate front column up
                if self.cube.start_column_rotation(-1, rotation_column=-1):
                    self.animation_timer.start()
            elif event.key() == Qt.Key_G:  # Rotate front column down
                if self.cube.start_column_rotation(1, rotation_column=-1):
                    self.animation_timer.start()



    def start_rotation(self, axis, angle):
        if self.cube.animate_rotation(axis, angle):
            self.animation_timer.start()
            time.sleep(0.001)

    def update_animation(self):
        if not self.cube.update_animation():
            self.animation_timer.stop()
        time.sleep(0.001)
        self.update()

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        if event.button() == Qt.LeftButton:
            if not self.cube.handle_click(x, y):
                self.mouse_pressed = True
                self.last_pos = event.pos()
        if event.button() == Qt.RightButton:
            if not self.cube.handle_click(x, y, is_right_click=True):
                self.right_mouse_pressed = True
                self.last_pos = event.pos()

        self.update()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed and not self.cube.is_animating:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            
            # Scale the rotation (adjust these values to change rotation sensitivity)
            rotation_scale = 0.5
            x_rotation = dy * rotation_scale
            y_rotation = dx * rotation_scale
            
            # Update cube rotation
            self.cube.rotation[0] += x_rotation
            self.cube.rotation[1] += y_rotation
            self.cube.target_rotation = self.cube.rotation.copy()
            
            self.last_pos = event.pos()
            self.update()


    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.9, 0.9, 0.9, 1.0)

    def wheelEvent(self, event):
        zoom_speed = 0.5
        delta = event.angleDelta().y() / 120.0
        self.zoom_level += delta * zoom_speed
        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 50.0)
        glTranslatef(0.0, 0.0, self.zoom_level)
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width()/self.height(), 0.1, 50.0)
        glTranslatef(0.0, 0.0, self.zoom_level)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.cube.draw()

