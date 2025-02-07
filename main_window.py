import sys
import json
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QWidget, QMenuBar, QMenu, QAction, QFileDialog, QApplication, QTextEdit, QLabel)
from PyQt5.QtCore import QTimer
from gl_widget import GLWidget
from colors import CubeColor
from cube_model import RubiksCube
import rubiksolver
import threading
import os

class RubiksWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rubiks Cube State Input')
        self.setGeometry(100, 100, 800, 600)
        self.nav_buttons = {}
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.check_animation_state)
        self.animation_timer.start(16)  # ~60 FPS check rate
        
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        view_menu = menubar.addMenu('View')  # Add new View menu
        
        solve_action = QAction('Solve', self)
        solve_action.setShortcut('Ctrl+R')
        solve_action.triggered.connect(self.solve_cube)
        file_menu.addAction(solve_action)
        
        # Add menu actions
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_cube_state)

        load_action = QAction('Load', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_cube_state)
        file_menu.addAction(load_action)

        file_menu.addAction(save_action)        
        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.clear_cube)
        file_menu.addAction(clear_action)

        debug_action = QAction('Debug Cube State', self)
        debug_action.triggered.connect(self.print_cube_state)
        view_menu.addAction(debug_action)

        debug_action = QAction('Test Dict Creation', self)
        debug_action.triggered.connect(self.convert_cube_to_dict)
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
        
        '''debug_window = QTextEdit()
        debug_window.setReadOnly(True)
        debug_window.setFixedWidth(10)'''
        
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
        #layout.addWidget(debug_window)
        
        solution_controls = self.setup_solution_controls()
        layout.addWidget(solution_controls)

        # Add GL widget
        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget)

    def check_animation_state(self):
        """Check if cube is currently animating and update button states"""
        is_animating = (self.gl_widget.cube.is_animating or 
                       self.gl_widget.cube.rotating_row or 
                       self.gl_widget.cube.rotating_column or 
                       self.gl_widget.cube.rotating_face)
    
        # Update navigation buttons
        for btn in self.nav_buttons.values():
            btn.setEnabled(not is_animating)
    
        # Update solution control buttons
        if hasattr(self, 'next_step_btn'):
            self.next_step_btn.setEnabled(not is_animating)
        if hasattr(self, 'prev_step_btn'):
            self.prev_step_btn.setEnabled(not is_animating)
        if hasattr(self, 'reset_solution_btn'):
            self.reset_solution_btn.setEnabled(not is_animating)        


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

    def convert_cube_to_dict(self):
        """Convert the cube state to a dictionary mapping coordinates to colors in Kociemba order"""
        cube = self.gl_widget.cube
        # Initialize dict with faces in Kociemba order (URFDLB)
        cube_dict = {
            'up': {},
            'right': {},
            'front': {},
            'down': {},
            'left': {},
            'back': {}
        }
    
        # Mapping from 3D coordinates to 2D face positions
        # Modified to ensure correct Kociemba ordering within each face
        face_mappings = {
            'up': {(x, 1, z): (z+1, x+1) for x in range(-1, 2) for z in range(-1, 2)},  # Read from top-left
            'right': {(1, y, z): (-y+1, -z+1) for y in range(1, -2, -1) for z in range(-1, 2)},
            'front': {(x, y, 1): (-y+1, x+1) for y in range(1, -2, -1) for x in range(-1, 2)},
            'down': {(x, -1, z): (-z+1, x+1) for x in range(-1, 2) for z in range(1, -2, -1)},  # Bottom face from top
            'left': {(-1, y, z): (-y+1, z+1) for y in range(1, -2, -1) for z in range(1, -2, -1)},
            'back': {(x, y, -1): (-y+1, -x+1) for y in range(1, -2, -1) for x in range(-1, 2)}
        }
    
        # Fill the dictionary
        for pos, cubelet in cube.cubelets.items():
            x, y, z = pos
            for face_name, mapping in face_mappings.items():
                if pos in mapping:
                    if face_name in cubelet['colors']:
                        row, col = mapping[pos]
                        # Convert position to string key
                        pos_key = f"{col},{row}"
                        cube_dict[face_name][pos_key] = cubelet['colors'][face_name].name
    
        # Clean and sort the dictionary
        clean_dict = {}
        for face in cube_dict:
            sorted_dict = dict(sorted(cube_dict[face].items(), 
                                    key=lambda y: (int(y[0].split(',')[1]), int(y[0].split(',')[0]))))
            clean_dict[face] = sorted_dict
    
        return clean_dict
        
    def save_cube_state(self):
        """Save the current cube state to a JSON file"""
    
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Cube State",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
    
        if filename:
            # Use the instance method to get the cube dictionary
            cube_dict = self.convert_cube_to_dict()
        
            # Save to file
            if not filename.endswith(".json"):
                filename+=".json"
            with open(filename, 'w') as f:
                json.dump(cube_dict, f, indent=3)
            print(f"Saved cube state to {filename}")

    def load_cube_state(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Cube State", "", "JSON Files (*.json);;All Files (*)")
    
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                state_dict = json.load(f)
        
            self.gl_widget.cube = RubiksCube()
        
            face_mappings = {
                'up': lambda x, z: (x-1, 1, z-1),
                'right': lambda z, y: (1, -y+1, -z+1),
                'front': lambda x, y: (x-1, -y+1, 1),
                'down': lambda x, z: (x-1, -1, -z+1),
                'left': lambda z, y: (-1, -y+1, z-1),
                'back': lambda x, y: (-x+1, -y+1, -1)
            }
        
            for face_name, face_dict in state_dict.items():
                for pos_str, color_name in face_dict.items():
                    x, y = map(int, pos_str.split(','))
                    coords = face_mappings[face_name](x, y)
                    self.gl_widget.cube.cubelets[coords]['colors'][face_name] = CubeColor[color_name]
        
            self.gl_widget.update()
        
        except Exception as e:
            print(f"Error loading cube state: {e}")
            return
        # Only tries to solve if it's been initialized
        exists = os.path.exists("tables.json")
        if exists:
            self.solve_cube()

    def save_state(self):
        state = self.gl_widget.cube.get_cube_state()
        print("Saving cube state:")
        for face_name, colors in state.items():
            print(f"{face_name}: {[c.name for c in colors]}")
    
    def clear_cube(self):
        print("Cube is being cleared")
        self.gl_widget.cube = RubiksCube()  # Reset cube state
        self.gl_widget.zoom_level = -15     # Reset zoom to default
        self.gl_widget.cube.rotation = [30, 45, 0]  # Reset rotation to starting position
        self.gl_widget.cube.target_rotation = [30, 45, 0]  # Reset target rotation
        self.gl_widget.update()
    
    def set_color(self, color: CubeColor):
        self.gl_widget.cube.set_selected_color(color)
        # Only tries to solve if it's been initialized
        exists = os.path.exists("tables.json")
        if exists:
            self.solve_cube()

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

    def setup_solution_controls(self):
        """Add solution control buttons"""
        solution_controls = QWidget()
        solution_controls.setMaximumHeight(40)
        solution_layout = QHBoxLayout(solution_controls)
        solution_layout.setSpacing(2)
        solution_layout.setContentsMargins(5, 0, 5, 0)
        
        # Add solution control buttons
        self.prev_step_btn = QPushButton('←')
        self.prev_step_btn.setFixedSize(30, 30)
        self.prev_step_btn.clicked.connect(self.previous_step)
        self.prev_step_btn.setEnabled(False)
    
        self.next_step_btn = QPushButton('→')
        self.next_step_btn.setFixedSize(30, 30)
        self.next_step_btn.clicked.connect(self.next_step)
        self.next_step_btn.setEnabled(False)
    
        self.reset_solution_btn = QPushButton('Reset')
        self.reset_solution_btn.setFixedSize(60, 30)
        self.reset_solution_btn.clicked.connect(self.clear_cube)
    
        # Add solution status label
        self.solution_status = QLabel("No solution available")
        self.solution_status.setStyleSheet("color: red;")
    
        solution_layout.addWidget(self.prev_step_btn)
        solution_layout.addWidget(self.next_step_btn)
        solution_layout.addWidget(self.reset_solution_btn)
        solution_layout.addWidget(self.solution_status)
        solution_layout.addStretch()
    
        return solution_controls
    
    def solve_cube(self):
        """Modified solve_cube method to handle solution animation"""
        
        exists = os.path.exists("tables.json")
        if not exists:
            self.solution_status.setText("Tables.json does not exist; it will be generated.  Be patient.")
            self.solution_status.setStyleSheet("color: red;")
            QApplication.processEvents()

        try:
            cube_dict = self.convert_cube_to_dict()
            solution = rubiksolver.solve_cube(cube_dict)
            if solution:
                self.gl_widget.cube.set_solution_steps(solution)
                self.gl_widget.cube.start_solution_animation()
                self.next_step_btn.setEnabled(True)
                self.prev_step_btn.setEnabled(True)
                self.solution_status.setText("Solution available")
                self.solution_status.setStyleSheet("color: green;")
            else:
                self.next_step_btn.setEnabled(False)
                self.prev_step_btn.setEnabled(False)
                self.solution_status.setText("No solution available")
                self.solution_status.setStyleSheet("color: red;")
        except Exception:
            self.next_step_btn.setEnabled(False)
            self.prev_step_btn.setEnabled(False)
            self.solution_status.setText("Invalid cube state")
            self.solution_status.setStyleSheet("color: red;")
        
    def previous_step(self):
        """Execute previous solution step"""
        print("Window: Previous step button pressed")
        if not self.gl_widget.cube.is_animating:
            if self.gl_widget.cube.previous_solution_step():
                print("Window: Starting animation timer")
                self.gl_widget.animation_timer.start()
                self.next_step_btn.setEnabled(True)
                self.gl_widget.update()
            else:
                self.prev_step_btn.setEnabled(False)
    
    def reset_solution(self):
        """Reset the solution animation"""
        self.gl_widget.cube.reset_solution()
        self.next_step_btn.setEnabled(True)
        self.prev_step_btn.setEnabled(False)
        self.gl_widget.update()
        
    def next_step(self):
        """Execute next solution step"""
        print("Window: Next step button pressed")
        if self.gl_widget.cube.next_solution_step():
            print("Window: Starting animation timer")
            self.gl_widget.animation_timer.start()
            self.gl_widget.update()        

