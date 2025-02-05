class RubiksCube:
    def __init__(self, cube_state):
        self.state = cube_state.copy()
        self.moves = []
        self.solution = {
            "cross": [],
            "f2l": [],
            "oll": [],
            "pll": []
        }
        
    def get_color(self, face, x, y):
        return self.state[face][f"{x},{y}"]
    
    def set_color(self, face, x, y, color):
        self.state[face][f"{x},{y}"] = color
    
    def get_center_color(self, face):
        return self.get_color(face, 1, 1)
    
    def rotate_face_clockwise(self, face):
        old_state = {k: v for k, v in self.state[face].items()}
        
        # Rotate corners
        self.state[face]["0,0"] = old_state["2,0"]
        self.state[face]["0,2"] = old_state["0,0"]
        self.state[face]["2,2"] = old_state["0,2"]
        self.state[face]["2,0"] = old_state["2,2"]
        
        # Rotate edges
        self.state[face]["0,1"] = old_state["1,0"]
        self.state[face]["1,2"] = old_state["0,1"]
        self.state[face]["2,1"] = old_state["1,2"]
        self.state[face]["1,0"] = old_state["2,1"]
        
        # Update adjacent faces
        self._update_adjacent_faces(face, "clockwise")
        self.moves.append(f"{face}_CW")
    
    def rotate_face_counterclockwise(self, face):
        for _ in range(3):  # Three clockwise rotations = one counterclockwise
            self.rotate_face_clockwise(face)
        self.moves.pop()  # Remove the three clockwise moves
        self.moves.append(f"{face}_CCW")
    
    def _update_adjacent_faces(self, face, direction):
        adjacent_faces = {
            "front": {
                "top": [(0,2), (1,2), (2,2)],
                "right": [(0,0), (0,1), (0,2)],
                "bottom": [(2,0), (1,0), (0,0)],
                "left": [(2,0), (2,1), (2,2)]
            },
            # Add similar mappings for other faces
        }
        
        if face in adjacent_faces:
            faces_order = ["top", "right", "bottom", "left"]
            if direction == "counterclockwise":
                faces_order.reverse()
            
            # Save the first face's values
            first_face = faces_order[0]
            temp_values = [self.get_color(first_face, x, y) 
                         for x, y in adjacent_faces[face][first_face]]
            
            # Rotate values around adjacent faces
            for i in range(len(faces_order)-1):
                current_face = faces_order[i]
                next_face = faces_order[i+1]
                
                current_coords = adjacent_faces[face][current_face]
                next_coords = adjacent_faces[face][next_face]
                
                for j in range(len(current_coords)):
                    nx, ny = next_coords[j]
                    self.set_color(current_face, *current_coords[j],
                                 self.get_color(next_face, nx, ny))
            
            # Place saved values in the last face
            last_face = faces_order[-1]
            last_coords = adjacent_faces[face][last_face]
            for i, (x, y) in enumerate(last_coords):
                self.set_color(last_face, x, y, temp_values[i])

    def solve_cross(self):
        """Solve the white cross on the bottom face."""
        target_color = self.get_center_color("bottom")
        edges = self._find_edges(target_color)
        
        for edge in edges:
            if edge["face"] == "bottom":
                if self.get_color(edge["adjacent_face"], *edge["adjacent_coords"]) != \
                   self.get_center_color(edge["adjacent_face"]):
                    # Edge is in bottom face but needs orientation
                    self._orient_cross_edge(edge)
            else:
                # Move edge to bottom face
                self._move_edge_to_bottom(edge)
        
        self.solution["cross"] = self.moves.copy()
        self.moves = []

    def _find_edges(self, color):
        """Find all edges of a specific color."""
        edges = []
        for face in self.state:
            # Check middle edges of each face
            edge_positions = [(0,1), (1,0), (1,2), (2,1)]
            for x, y in edge_positions:
                if self.get_color(face, x, y) == color:
                    adjacent = self._get_adjacent_edge(face, x, y)
                    edges.append({
                        "face": face,
                        "coords": (x, y),
                        "adjacent_face": adjacent["face"],
                        "adjacent_coords": adjacent["coords"]
                    })
        return edges

    def _get_adjacent_edge(self, face, x, y):
        """Get the adjacent face and coordinates for an edge piece."""
        # Implementation would map edge positions to adjacent faces
        # This is a simplified version
        return {
            "face": "front" if face == "top" else "top",
            "coords": (0, 1) if face == "top" else (2, 1)
        }

    def solve_f2l(self):
        """Solve the first two layers."""
        corners = self._find_f2l_pairs()
        for corner in corners:
            self._solve_f2l_pair(corner)
        
        self.solution["f2l"] = self.moves.copy()
        self.moves = []

    def solve_oll(self):
        """Orient the last layer."""
        # Identify OLL case
        case = self._identify_oll_case()
        
        # Apply algorithm for the specific case
        self._apply_oll_algorithm(case)
        
        self.solution["oll"] = self.moves.copy()
        self.moves = []

    def solve_pll(self):
        """Permute the last layer."""
        # Identify PLL case
        case = self._identify_pll_case()
        
        # Apply algorithm for the specific case
        self._apply_pll_algorithm(case)
        
        self.solution["pll"] = self.moves.copy()
        self.moves = []

    def _identify_oll_case(self):
        """
        Identify which OLL case we have.
        Returns a tuple of (case_number, rotation_needed)
        """
        top_face = [[self.get_color("top", x, y) for y in range(3)] for x in range(3)]
        top_color = self.get_center_color("top")
        
        # Get edge orientations (top color or not)
        edges = [
            top_face[0][1] == top_color,  # Top edge
            top_face[1][2] == top_color,  # Right edge
            top_face[2][1] == top_color,  # Bottom edge
            top_face[1][0] == top_color   # Left edge
        ]
        
        # Get corner orientations (top color or not)
        corners = [
            top_face[0][0] == top_color,  # Top-left
            top_face[0][2] == top_color,  # Top-right
            top_face[2][2] == top_color,  # Bottom-right
            top_face[2][0] == top_color   # Bottom-left
        ]
        
        # Check for common OLL patterns
        if all(corners) and all(edges):
            return (0, 0)  # Already solved
        
        # Dot cases (no edges oriented)
        if not any(edges):
            if sum(corners) == 0:
                return (1, 0)  # Full dot
            if sum(corners) == 1:
                return (2, self._find_rotation_for_pattern(corners, [True, False, False, False]))
        
        # Line cases (two edges oriented)
        if sum(edges) == 2:
            if edges[0] and edges[2]:
                return (3, 0)  # Vertical line
            if edges[1] and edges[3]:
                return (4, 0)  # Horizontal line
        
        # L cases (two adjacent edges oriented)
        if sum(edges) == 2 and sum(corners) == 1:
            for i in range(4):
                if edges[i] and edges[(i+1)%4] and corners[i]:
                    return (5, i)
        
        return (6, 0)  # Default case

    def _identify_pll_case(self):
        """
        Identify which PLL case we have.
        Returns a tuple of (case_number, rotation_needed)
        """
        # Get the colors of all edges and corners in the top layer
        edge_colors = []
        corner_colors = []
        faces = ["front", "right", "back", "left"]
        
        for i, face in enumerate(faces):
            # Get edge color
            edge_colors.append(self.get_color(face, 0, 1))
            # Get corner colors (both sides)
            corner_colors.append((
                self.get_color(face, 0, 0),
                self.get_color(faces[(i-1)%4], 0, 2)
            ))
        
        # Check for solved state
        if all(self.get_color(face, 0, 1) == self.get_center_color(face) for face in faces):
            return (0, 0)  # Already solved
        
        # Adjacent corner swap
        adj_corner_swap = False
        for i in range(4):
            if (corner_colors[i] == corner_colors[(i+1)%4][::-1] and
                corner_colors[(i+2)%4] == corner_colors[(i+3)%4]):
                adj_corner_swap = True
                return (1, i)  # A perm
        
        # Diagonal corner swap
        if (corner_colors[0] == corner_colors[2][::-1] and
            corner_colors[1] == corner_colors[3][::-1]):
            return (2, 0)  # E perm
        
        # Edge cycle cases
        edge_matches = [edge_colors[i] == self.get_center_color(faces[i]) for i in range(4)]
        if sum(edge_matches) == 2:
            for i in range(4):
                if edge_matches[i] and edge_matches[(i+2)%4]:
                    return (3, i)  # U perm
        
        return (4, 0)  # Default case (Z perm)

    def _apply_oll_algorithm(self, case_and_rotation):
        """Apply the algorithm for the specific OLL case."""
        case, rotation = case_and_rotation
        
        # Rotate top face to align case if needed
        for _ in range(rotation):
            self.rotate_face_clockwise("top")
        
        # Dictionary of OLL algorithms
        algorithms = {
            0: [],  # Already solved
            1: [  # Dot case
                ("front", "CW"), ("right", "CW"), ("top", "CW"),
                ("right", "CCW"), ("top", "CCW"), ("front", "CCW")
            ],
            2: [  # Antisune
                ("right", "CW"), ("top", "CW"), ("right", "CCW"),
                ("top", "CW"), ("right", "CW"), ("top", "CW"),
                ("top", "CW"), ("right", "CCW")
            ],
            3: [  # Vertical line
                ("front", "CW"), ("right", "CW"), ("top", "CW"),
                ("right", "CCW"), ("top", "CCW"), ("front", "CCW")
            ],
            4: [  # Horizontal line
                ("right", "CW"), ("top", "CW"), ("top", "CW"),
                ("right", "CCW"), ("right", "CCW"), ("top", "CW"),
                ("right", "CW"), ("top", "CCW"), ("right", "CCW")
            ],
            5: [  # L case
                ("right", "CW"), ("top", "CW"), ("right", "CCW"),
                ("top", "CCW"), ("right", "CW"), ("top", "CW"),
                ("right", "CCW")
            ],
            6: [  # Default case (Sune)
                ("right", "CW"), ("top", "CW"), ("right", "CCW"),
                ("top", "CW"), ("right", "CW"), ("top", "top"),
                ("right", "CCW")
            ]
        }
        
        # Execute the algorithm
        for face, direction in algorithms[case]:
            if direction == "CW":
                self.rotate_face_clockwise(face)
            elif direction == "CCW":
                self.rotate_face_counterclockwise(face)
            else:  # Double move
                self.rotate_face_clockwise(face)
                self.rotate_face_clockwise(face)

    def _apply_pll_algorithm(self, case_and_rotation):
        """Apply the algorithm for the specific PLL case."""
        case, rotation = case_and_rotation
        
        # Rotate top face to align case if needed
        for _ in range(rotation):
            self.rotate_face_clockwise("top")
        
        # Dictionary of PLL algorithms
        algorithms = {
            0: [],  # Already solved
            1: [  # A perm (adjacent corner swap)
                ("right", "CCW"), ("front", "CW"), ("right", "CCW"),
                ("back", "CW"), ("back", "CW"), ("right", "CW"),
                ("front", "CCW"), ("right", "CCW"), ("back", "CW"),
                ("back", "CW"), ("right", "CW"), ("right", "CW")
            ],
            2: [  # E perm (diagonal corner swap)
                ("right", "CW"), ("back", "CW"), ("right", "CCW"),
                ("front", "CCW"), ("right", "CW"), ("back", "CCW"),
                ("right", "CCW"), ("front", "CW"), ("right", "CW"),
                ("back", "CW"), ("right", "CCW"), ("front", "CCW"),
                ("right", "CW"), ("back", "CCW"), ("right", "CCW"),
                ("front", "CW")
            ],
            3: [  # U perm (3-edge cycle)
                ("right", "CW"), ("right", "CW"), ("top", "CW"),
                ("right", "CW"), ("right", "CW"), ("top", "CCW"),
                ("right", "CW"), ("right", "CW"), ("top", "CCW"),
                ("right", "CW"), ("right", "CW")
            ],
            4: [  # Z perm (edge cycle)
                ("right", "CW"), ("top", "CW"), ("right", "CCW"),
                ("top", "CW"), ("right", "CW"), ("top", "top"),
                ("right", "CCW"), ("top", "CCW"), ("right", "CCW"),
                ("right", "CW"), ("top", "CCW"), ("right", "CCW")
            ]
        }
        
        # Execute the algorithm
        for face, direction in algorithms[case]:
            if direction == "CW":
                self.rotate_face_clockwise(face)
            elif direction == "CCW":
                self.rotate_face_counterclockwise(face)
            else:  # Double move
                self.rotate_face_clockwise(face)
                self.rotate_face_clockwise(face)

    def _move_edge_to_bottom(self, edge):
        """Move an edge piece to the bottom face in the correct position."""
        source_face = edge["face"]
        target_face = edge["adjacent_face"]
        source_coords = edge["coords"]
        target_coords = edge["adjacent_coords"]
    
        # Get the center colors to determine the correct position
        edge_color = self.get_color(source_face, *source_coords)
        adjacent_color = self.get_color(target_face, *target_coords)
    
        # First, get the piece to the top layer if it's not already there
        if source_face != "top" and source_face != "bottom":
            if source_coords[1] == 1:  # Middle layer edge
                # Setup moves to get to top layer
                if source_coords[0] == 0:  # Left side
                    self.rotate_face_clockwise(source_face)
                    self.rotate_face_clockwise("top")
                    self.rotate_face_counterclockwise(source_face)
                else:  # Right side
                    self.rotate_face_counterclockwise(source_face)
                    self.rotate_face_counterclockwise("top")
                    self.rotate_face_clockwise(source_face)
    
        # Now the piece is in the top layer, rotate to correct position
        target_position = self._find_matching_center(edge_color)
        current_position = self._get_top_face_position(source_face)
    
        # Rotate top face to align with target position
        rotations_needed = (target_position - current_position) % 4
        for _ in range(rotations_needed):
            self.rotate_face_clockwise("top")
    
        # Insert into bottom layer with appropriate algorithm
        self._insert_edge_to_bottom(target_position)

    def _orient_cross_edge(self, edge):
        """Orient a cross edge that is in the bottom layer but incorrectly oriented."""
        face = edge["adjacent_face"]
    
        # Bring edge to top layer
        for _ in range(2):  # Double turn of both involved faces
            self.rotate_face_clockwise(face)
            self.rotate_face_clockwise("bottom")
    
        # Now the edge is in top layer, reinsert correctly
        self._insert_edge_to_bottom(self._get_face_position(face))

    def _find_matching_center(self, color):
        """Find which face has a center matching the given color."""
        faces = ["front", "right", "back", "left"]
        for i, face in enumerate(faces):
            if self.get_center_color(face) == color:
                return i
        return -1

    def _get_top_face_position(self, face):
        """Convert face name to position number (0=front, 1=right, 2=back, 3=left)."""
        positions = {"front": 0, "right": 1, "back": 2, "left": 3}
        return positions.get(face, -1)

    def _get_face_position(self, face):
        """Get the numerical position (0-3) for a given face name."""
        positions = {"front": 0, "right": 1, "back": 2, "left": 3}
        return positions.get(face, -1)

    def _insert_edge_to_bottom(self, position):
        """Insert an edge from top layer to bottom layer at given position."""
        faces = ["front", "right", "back", "left"]
        face = faces[position]
    
        # Double turn to insert
        for _ in range(2):
            self.rotate_face_clockwise(face)

    def _find_f2l_pairs(self):
        """Find all corner-edge pairs for F2L."""
        bottom_color = self.get_center_color("bottom")
        pairs = []
        
        # Find all corners that belong to F2L
        for face in ["front", "right", "back", "left"]:
            # Check bottom corners of each face
            if (self.get_color(face, 2, 0) == bottom_color or
                self.get_color("bottom", 0, 0) == bottom_color or
                self.get_color(self._get_left_face(face), 2, 2) == bottom_color):
                
                pairs.append(self._get_f2l_pair_info(face, "bottom"))
            
            # Check top corners that might belong to F2L
            if (self.get_color(face, 0, 0) == bottom_color or
                self.get_color("top", 2, 0) == bottom_color or
                self.get_color(self._get_left_face(face), 0, 2) == bottom_color):
                
                pairs.append(self._get_f2l_pair_info(face, "top"))
        
        return pairs
    
    def _get_f2l_pair_info(self, face, layer):
        """Get information about an F2L pair given a face and layer."""
        info = {
            "corner_face": face,
            "corner_layer": layer,
            "corner_colors": self._get_corner_colors(face, layer),
            "edge_colors": self._find_matching_edge(face, layer)
        }
        return info
    
    def _get_corner_colors(self, face, layer):
        """Get the colors of a corner piece."""
        colors = {}
        y = 0 if layer == "top" else 2
        
        colors[face] = self.get_color(face, y, 0)
        colors[self._get_left_face(face)] = self.get_color(self._get_left_face(face), y, 2)
        colors[layer] = self.get_color(layer, 2 if layer == "top" else 0, 0)
        
        return colors
    
    def _find_matching_edge(self, face, layer):
        """Find the matching edge piece for an F2L pair."""
        corner_colors = set(self._get_corner_colors(face, layer).values())
        corner_colors.remove(self.get_center_color("bottom"))  # Remove white/yellow
        
        # Check all edges
        for check_face in ["front", "right", "back", "left"]:
            for y in [0, 2]:  # Check top and bottom edges
                edge_colors = self._get_edge_colors(check_face, y)
                if set(edge_colors.values()) == corner_colors:
                    return edge_colors
        
        return None
    
    def _get_edge_colors(self, face, y):
        """Get the colors of an edge piece."""
        colors = {}
        colors[face] = self.get_color(face, y, 1)
        if y == 0:
            colors["top"] = self.get_color("top", 2, 1)
        else:
            colors["bottom"] = self.get_color("bottom", 0, 1)
        return colors
    
    def _get_left_face(self, face):
        """Get the face to the left of the given face."""
        faces = ["front", "right", "back", "left"]
        idx = faces.index(face)
        return faces[(idx - 1) % 4]
    
    def _get_right_face(self, face):
        """Get the face to the right of the given face."""
        faces = ["front", "right", "back", "left"]
        idx = faces.index(face)
        return faces[(idx + 1) % 4]
    
    def _solve_f2l_pair(self, pair_info):
        """Solve a single F2L pair."""
        # Get corner position and orientation
        corner_face = pair_info["corner_face"]
        corner_layer = pair_info["corner_layer"]
        
        # Get edge position and relationship to corner
        edge_colors = pair_info["edge_colors"]
        
        # If corner is in top layer, align and insert
        if corner_layer == "top":
            self._insert_f2l_pair_from_top(corner_face, edge_colors)
        else:
            # Corner in bottom layer - extract if needed and then solve
            self._extract_and_insert_f2l_pair(corner_face, edge_colors)
    
    def _insert_f2l_pair_from_top(self, corner_face, edge_colors):
        """Insert an F2L pair when the corner is in the top layer."""
        # Basic insertion algorithm (simplified)
        self.rotate_face_clockwise(corner_face)  # R
        self.rotate_face_clockwise("top")        # U
        self.rotate_face_counterclockwise(corner_face)  # R'
    
    def _extract_and_insert_f2l_pair(self, corner_face, edge_colors):
        """Extract a corner from bottom layer and insert the pair."""
        # Basic extraction algorithm (simplified)
        self.rotate_face_clockwise("top")        # U
        self.rotate_face_clockwise(corner_face)  # R
        self.rotate_face_counterclockwise("top") # U'
        self.rotate_face_counterclockwise(corner_face)  # R'
        
        # Now the corner is in top layer, insert normally
        self._insert_f2l_pair_from_top(corner_face, edge_colors)

    def _find_rotation_for_pattern(self, current_pattern, target_pattern):
        for i in range(4):  # Try all possible rotations
            # Check if patterns match after i rotations
            rotated = current_pattern[i:] + current_pattern[:i]
            if rotated == target_pattern:
                return i
        return 0  # Default to no rotation if no match found

def validate_cube_state(cube_state):
    """
    Validates if a given cube state represents a valid 3x3 Rubik's cube.
    Returns (is_valid: bool, error_message: str)
    """
    # Check basic structure
    if not isinstance(cube_state, dict):
        return False, "Cube state must be a dictionary"
        
    required_faces = {"front", "back", "top", "bottom", "left", "right"}
    if set(cube_state.keys()) != required_faces:
        return False, "Must have exactly 6 faces: front, back, top, bottom, left, right"
    
    # Validate each face has 9 stickers in correct positions
    required_positions = {f"{x},{y}" for x in range(3) for y in range(3)}
    for face, stickers in cube_state.items():
        if set(stickers.keys()) != required_positions:
            return False, f"Face {face} missing required sticker positions"
            
    # Count colors
    color_count = {}
    centers = {}
    for face, stickers in cube_state.items():
        # Record center color
        centers[face] = stickers["1,1"]
        for pos, color in stickers.items():
            color_count[color] = color_count.get(color, 0) + 1
            
    # Each color should appear exactly 9 times
    if not all(count == 9 for count in color_count.values()):
        color_counts = [f"{color}: {count}" for color, count in sorted(color_count.items())]
        return False, f"Invalid color counts: {', '.join(color_counts)}"
        
    # Centers must all be different
    if len(set(centers.values())) != 6:
        return False, "Center pieces must all have different colors"

    return True, "Valid cube state"

def solve_cube(cube_state):
    """
    Solves a Rubik's cube using the CFOP method (Fridrich method)
    
    Args:
        cube_state (dict): Dictionary containing the current state of the cube
    
    Returns:
        dict: Dictionary containing the solution steps organized by phase
    """
    cube = RubiksCube(cube_state)
    
    # Solve using CFOP method
    cube.solve_cross()  # White cross
    cube.solve_f2l()    # First two layers
    cube.solve_oll()    # Orientation of last layer
    cube.solve_pll()    # Permutation of last layer
    
    return cube.solution
