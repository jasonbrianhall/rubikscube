# Interactive Rubik's Cube Simulator

A Python-based interactive Rubik's Cube simulator built with PyQt5 and OpenGL. This application provides a 3D visualization of a Rubik's cube that users can manipulate, color, and solve.

## Features

- Full 3D visualization of a Rubik's cube
- Interactive rotation controls using keyboard and mouse
- Face coloring functionality
- Support for multiple rotation types:
  - Row rotations (top and bottom)
  - Column rotations (left and right)
  - Face rotations (front and back)
- Animation system for smooth rotations
- Solution steps execution system

## Requirements

- Python 3.x
- PyQt5
- PyOpenGL

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jasonbrianhall/rubikscube.git
cd rubikscube
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application using:
```bash
python main.py
```

### Controls

#### Keyboard Controls:

- **Cube Rotation:**
  - Arrow Left/Right: Rotate entire cube horizontally
  - Arrow Up/Down: Rotate entire cube vertically

- **Row Rotations:**
  - A: Rotate top row counterclockwise
  - D: Rotate top row clockwise
  - H: Rotate bottom row counterclockwise
  - F: Rotate bottom row clockwise

- **Column Rotations:**
  - W: Rotate front column up
  - S: Rotate front column down
  - T: Rotate back column up
  - G: Rotate back column down

#### Mouse Controls:

- Click on any face to apply the currently selected color
- Click and drag to rotate the cube

## Project Structure

- `main.py`: Application entry point
- `main_window.py`: Main window UI implementation
- `gl_widget.py`: OpenGL widget for 3D rendering
- `cube_model.py`: Rubik's cube model and logic
- `colors.py`: Color definitions and enums

## Technical Details

### Cube Model

The cube is modeled as 27 individual cubelets (3x3x3), each with up to six faces. The state of each cubelet is tracked using:
- Position coordinates (x, y, z)
- Face colors
- Face visibility (exterior vs interior)

### Rotation System

The application supports three types of rotations:
1. Row rotations (horizontal layers)
2. Column rotations (vertical layers)
3. Face rotations (front/back faces)

Each rotation is animated smoothly using a timer-based animation system.

### Color System

Colors are implemented using an Enum class that defines:
- Standard cube colors (Red, Yellow, Green, Blue, Orange, White)
- Special states (Unassigned, Interior)

### Rendering

The cube is rendered using OpenGL with:
- Perspective projection
- Depth testing
- Face culling
- Smooth animations
- Click detection for face coloring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Insert your chosen license here]

## Acknowledgments

This project was created as a demonstration of 3D graphics programming with Python and OpenGL, combining interactive graphics with a classic puzzle game.
