import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

pygame.init()
info = pygame.display.Info()
display = (info.current_w, info.current_h)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -15)

class Cube:
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.vertices = [
            [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1],
            [1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, 1, 1]
        ]
        self.surfaces = [
            [0, 1, 2, 3], [3, 2, 7, 6], [6, 7, 5, 4],
            [4, 5, 1, 0], [1, 5, 7, 2], [4, 0, 3, 6]
        ]
        self.edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        
        # Draw faces
        glBegin(GL_QUADS)
        for surface in self.surfaces:
            glColor3fv(self.color)
            for vertex in surface:
                glVertex3fv(np.array(self.vertices[vertex]) * 0.45)  # Slightly smaller cubes
        glEnd()
        
        # Draw black edges
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor3f(0, 0, 0)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(np.array(self.vertices[vertex]) * 0.45)
        glEnd()
        
        glPopMatrix()

class RubiksCube:
    def __init__(self):
        self.cubes = []
        self.rotation = [30, 45, 0]  # Initial rotation for isometric view
        self.colors = {
            'white': (1, 1, 1),
            'yellow': (1, 1, 0),
            'red': (1, 0, 0),
            'orange': (1, 0.5, 0),
            'blue': (0, 0, 1),
            'green': (0, 1, 0)
        }
        self._initialize_cubes()
        self._apply_initial_rotation()

    def _initialize_cubes(self):
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    pos = (x, y, z)
                    color = self._get_cube_color(pos)
                    self.cubes.append(Cube(pos, color))

    def _apply_initial_rotation(self):
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

    def _get_cube_color(self, pos):
        x, y, z = pos
        if z == 1:  # Front face
            return self.colors['white']
        elif z == -1:  # Back face
            return self.colors['yellow']
        elif y == 1:  # Top face
            return self.colors['red']
        elif y == -1:  # Bottom face
            return self.colors['orange']
        elif x == -1:  # Left face
            return self.colors['blue']
        elif x == 1:  # Right face
            return self.colors['green']
        return (0.8, 0.8, 0.8)  # Center cubes

    def rotate(self, axis, angle):
        self.rotation[axis] += angle
        glRotatef(angle, axis == 0, axis == 1, axis == 2)

    def draw(self):
        glClearColor(0.9, 0.9, 0.9, 1)  # Light gray background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for cube in self.cubes:
            cube.draw()

def main():
    rubiks_cube = RubiksCube()
    clock = pygame.time.Clock()
    rotation_speed = 5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rubiks_cube.rotate(1, -rotation_speed)
                elif event.key == pygame.K_RIGHT:
                    rubiks_cube.rotate(1, rotation_speed)
                elif event.key == pygame.K_UP:
                    rubiks_cube.rotate(0, -rotation_speed)
                elif event.key == pygame.K_DOWN:
                    rubiks_cube.rotate(0, rotation_speed)

        glEnable(GL_DEPTH_TEST)
        rubiks_cube.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
