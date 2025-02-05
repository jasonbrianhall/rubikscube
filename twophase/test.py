import json

class PruningTable:
    """
    Helper class to allow pruning to be used as though they were 2-D tables
    """

    def __init__(self, table, stride):
        self.table = table
        self.stride = stride

    def __getitem__(self, x):
        return self.table[x[0] * self.stride + x[1]]


class Tables:
    """
    Class for holding move and pruning tables in memory.

    Move tables are used for updating coordinate representation of cube when a
    particular move is applied.

    Pruning tables are used to obtain lower bounds for the number of moves
    required to reach a solution given a particular pair of coordinates.
    """

    _tables_loaded = False

    # 3^7 possible corner orientations
    TWIST = 2187
    # 2^11 possible edge flips
    FLIP = 2048
    # 12C4 possible positions of FR, FL, BL, BR
    UDSLICE = 495
    # 4! possible permutations of FR, FL, BL, BR
    EDGE4 = 24
    # 8! possible permutations of UR, UF, UL, UB, DR, DF, DL, DB in phase two
    EDGE8 = 40320
    # 8! possible permutations of the corners
    CORNER = 40320
    # 12! possible permutations of all edges
    EDGE = 479001600
    # 6*3 possible moves
    MOVES = 18

    def __init__(self):
        if not self._tables_loaded:
            self.load_tables()

    @classmethod
    def load_tables(cls):
        if os.path.isfile("tables.json"):
            with open("tables.json", "r") as f:
                tables = json.load(f)
            cls.twist_move = tables["twist_move"]
            cls.flip_move = tables["flip_move"]
            cls.udslice_move = tables["udslice_move"]
            cls.edge4_move = tables["edge4_move"]
            cls.edge8_move = tables["edge8_move"]
            cls.corner_move = tables["corner_move"]
            cls.udslice_twist_prune = PruningTable(
                tables["udslice_twist_prune"], cls.TWIST
            )
            cls.udslice_flip_prune = PruningTable(
                tables["udslice_flip_prune"], cls.FLIP
            )
            cls.edge4_edge8_prune = PruningTable(
                tables["edge4_edge8_prune"], cls.EDGE8
            )
            cls.edge4_corner_prune = PruningTable(
                tables["edge4_corner_prune"], cls.CORNER
            )
        else:
            # ----------  Phase 1 move tables  ---------- #
            cls.twist_move = cls.make_twist_table()
            cls.flip_move = cls.make_flip_table()
            cls.udslice_move = cls.make_udslice_table()

            # ----------  Phase 2 move tables  ---------- #
            cls.edge4_move = cls.make_edge4_table()
            cls.edge8_move = cls.make_edge8_table()
            cls.corner_move = cls.make_corner_table()

            # ----------  Phase 1 pruning tables  ---------- #
            cls.udslice_twist_prune = cls.make_udslice_twist_prune()
            cls.udslice_flip_prune = cls.make_udslice_flip_prune()

            # --------  Phase 2 pruning tables  ---------- #
            cls.edge4_edge8_prune = cls.make_edge4_edge8_prune()
            cls.edge4_corner_prune = cls.make_edge4_corner_prune()

            tables = {
                "twist_move": cls.twist_move,
                "flip_move": cls.flip_move,
                "udslice_move": cls.udslice_move,
                "edge4_move": cls.edge4_move,
                "edge8_move": cls.edge8_move,
                "corner_move": cls.corner_move,
                "udslice_twist_prune": cls.udslice_twist_prune.table,
                "udslice_flip_prune": cls.udslice_flip_prune.table,
                "edge4_edge8_prune": cls.edge4_edge8_prune.table,
                "edge4_corner_prune": cls.edge4_corner_prune.table,
            }
            with open("tables.json", "w") as f:
                json.dump(tables, f)

        cls._tables_loaded = True

    @classmethod
    def make_twist_table(cls):
        twist_move = [[0] * cls.MOVES for i in range(cls.TWIST)]
        a = CubieCube()
        for i in range(cls.TWIST):
            a.twist = i
            for j in range(6):
                for k in range(3):
                    a.corner_multiply(MOVE_CUBE[j])
                    twist_move[i][3 * j + k] = a.twist
                a.corner_multiply(MOVE_CUBE[j])
        return twist_move

    @classmethod
    def make_flip_table(cls):
        flip_move = [[0] * cls.MOVES for i in range(cls.FLIP)]
        a = CubieCube()
        for i in range(cls.FLIP):
            a.flip = i
            for j in range(6):
                for k in range(3):
                    a.edge_multiply(MOVE_CUBE[j])
                    flip_move[i][3 * j + k] = a.flip
                a.edge_multiply(MOVE_CUBE[j])
        return flip_move

    @classmethod
    def make_udslice_table(cls):
        udslice_move = [[0] * cls.MOVES for i in range(cls.UDSLICE)]
        a = CubieCube()
        for i in range(cls.UDSLICE):
            a.udslice = i
            for j in range(6):
                for k in range(3):
                    a.edge_multiply(MOVE_CUBE[j])
                    udslice_move[i][3 * j + k] = a.udslice
                a.edge_multiply(MOVE_CUBE[j])
        return udslice_move

    @classmethod
    def make_edge4_table(cls):
        edge4_move = [[0] * cls.MOVES for i in range(cls.EDGE4)]
        a = CubieCube()
        for i in range(cls.EDGE4):
            a.edge4 = i
            for j in range(6):
                for k in range(3):
                    a.edge_multiply(MOVE_CUBE[j])
                    if k % 2 == 0 and j % 3 != 0:
                        edge4_move[i][3 * j + k] = -1
                    else:
                        edge4_move[i][3 * j + k] = a.edge4
                a.edge_multiply(MOVE_CUBE[j])
        return edge4_move

    @classmethod
    def make_edge8_table(cls):
        edge8_move = [[0] * cls.MOVES for i in range(cls.EDGE8)]
        a = CubieCube()
        for i in range(cls.EDGE8):
            a.edge8 = i
            for j in range(6):
                for k in range(3):
                    a.edge_multiply(MOVE_CUBE[j])
                    if k % 2 == 0 and j % 3 != 0:
                        edge8_move[i][3 * j + k] = -1
                    else:
                        edge8_move[i][3 * j + k] = a.edge8
                a.edge_multiply(MOVE_CUBE[j])
        return edge8_move

    @classmethod
    def make_corner_table(cls):
        corner_move = [[0] * cls.MOVES for i in range(cls.CORNER)]
        a = CubieCube()
        for i in range(cls.CORNER):
            a.corner = i
            for j in range(6):
                for k in range(3):
                    a.corner_multiply(MOVE_CUBE[j])
                    if k % 2 == 0 and j % 3 != 0:
                        corner_move[i][3 * j + k] = -1
                    else:
                        corner_move[i][3 * j + k] = a.corner
                a.corner_multiply(MOVE_CUBE[j])
        return corner_move

    @classmethod
    def make_udslice_twist_prune(cls):
        udslice_twist_prune = [-1] * (cls.UDSLICE * cls.TWIST)
        udslice_twist_prune[0] = 0
        count, depth = 1, 0
        while count < cls.UDSLICE * cls.TWIST:
            for i in range(cls.UDSLICE * cls.TWIST):
                if udslice_twist_prune[i] == depth:
                    m = [
                        cls.udslice_move[i // cls.TWIST][j] * cls.TWIST
                        + cls.twist_move[i % cls.TWIST][j]
                        for j in range(18)
                    ]
                    for x in m:
                        if udslice_twist_prune[x] == -1:
                            count += 1
                            udslice_twist_prune[x] = depth + 1
            depth += 1
        return PruningTable(udslice_twist_prune, cls.TWIST)

    @classmethod
    def make_udslice_flip_prune(cls):
        udslice_flip_prune = [-1] * (cls.UDSLICE * cls.FLIP)
        udslice_flip_prune[0] = 0
        count, depth = 1, 0
        while count < cls.UDSLICE * cls.FLIP:
            for i in range(cls.UDSLICE * cls.FLIP):
                if udslice_flip_prune[i] == depth:
                    m = [
                        cls.udslice_move[i // cls.FLIP][j] * cls.FLIP
                        + cls.flip_move[i % cls.FLIP][j]
                        for j in range(18)
                    ]
                    for x in m:
                        if udslice_flip_prune[x] == -1:
                            count += 1
                            udslice_flip_prune[x] = depth + 1
            depth += 1
        return PruningTable(udslice_flip_prune, cls.FLIP)

    @classmethod
    def make_edge4_edge8_prune(cls):
        edge4_edge8_prune = [-1] * (cls.EDGE4 * cls.EDGE8)
        edge4_edge8_prune[0] = 0
        count, depth = 1, 0
        while count < cls.EDGE4 * cls.EDGE8:
            for i in range(cls.EDGE4 * cls.EDGE8):
                if edge4_edge8_prune[i] == depth:
                    m = [
                        cls.edge4_move[i // cls.EDGE8][j] * cls.EDGE8
                        + cls.edge8_move[i % cls.EDGE8][j]
                        for j in range(18)
                    ]
                    for x in m:
                        if edge4_edge8_prune[x] == -1:
                            count += 1
                            edge4_edge8_prune[x] = depth + 1
            depth += 1
        return PruningTable(edge4_edge8_prune, cls.EDGE8)

    @classmethod
    def make_edge4_corner_prune(cls):
        edge4_corner_prune = [-1] * (cls.EDGE4 * cls.CORNER)
        edge4_corner_prune[0] = 0
        count, depth = 1, 0
        while count < cls.EDGE4 * cls.CORNER:
            for i in range(cls.EDGE4 * cls.CORNER):
                if edge4_corner_prune[i] == depth:
                    m = [
                        cls.edge4_move[i // cls.CORNER][j] * cls.CORNER
                        + cls.corner_move[i % cls.CORNER][j]
                        for j in range(18)
                    ]
                    for x in m:
                        if edge4_corner_prune[x] == -1:
                            count += 1
                            edge4_corner_prune[x] = depth + 1
            depth += 1
        return PruningTable(edge4_corner_prune, cls.CORNER)

class CubieCube:
  # CubieCube implementation from previous code  
  ...
  
class FaceCube:
  # FaceCube implementation from previous code
  ...
  
class CoordCube:
  # CoordCube implementation from previous code
  ...
  
class SolutionManager:
    def __init__(self, facelets):
        """
        A utility class for managing the search for the solution.

        Parameters
        ----------
        facelets: str
            Starting position of the cube. Should be a 54 character string
            specifying the stickers on each face (in order U R F D L B),
            reading row by row from the top left hand corner to the bottom
            right
        """
        self.tables = Tables()

        self.facelets = facelets.upper()

        status = self.verify()
        if status:
            error_message = {
                -1: "each colour should appear exactly 9 times",
                -2: "not all edges exist exactly once",
                -3: "one edge should be flipped",
                -4: "not all corners exist exactly once",
                -5: "one corner should be twisted",
                -6: "two corners or edges should be exchanged",
            }
            raise ValueError("Invalid cube: {}".format(error_message[status]))

    def solve(self, max_length=25, timeout=float("inf")):
        """
        Solve the cube.

        This method implements back to back IDA* searches for phase 1 and phase
        2, returning the result. Can be called multiple times with decreasing
        max_length to try and find better solutions.

        Parameters
        ----------
        max_length: int, optional
            Upper bound for the allowed number of moves.
        max_time: int or float, optional
            Time at which to quit searching. Algorithm will quit when
            ``time.time() > max_time``.
        """
        # prepare for phase 1
        self._phase_1_initialise(max_length)
        self._allowed_length = max_length
        self._timeout = timeout

        for depth in range(self._allowed_length):
            n = self._phase_1_search(0, depth)
            if n >= 0:
                # solution found
                return self._solution_to_string(n)
            elif n == -2:
                # time limit exceeded
                return -2

        # no solution found
        return -1

    def verify(self):
        count = [0] * 6
        try:
            for char in self.facelets:
                count[Color[char]] += 1
        except (IndexError, ValueError):
            return -1
        for i in range(6):
            if count[i] != 9:
                return -1

        fc = FaceCube(self.facelets)
        cc = fc.to_cubiecube()

        return cc.verify()

    def _phase_1_initialise(self, max_length):
        # the lists 'axis' and 'power' will store the nth move (index of face
        # being turned stored in axis, number of clockwise quarter turns stored
        # in power). The nth move is stored in position n-1
        self.axis = [0] * max_length
        self.power = [0] * max_length

        # the lists twist, flip and udslice store the phase 1 coordinates after
        # n moves. position 0 stores the inital states, the coordinates after n
        # moves are stored in position n
        self.twist = [0] * max_length
        self.flip = [0] * max_length
        self.udslice = [0] * max_length

        # similarly to above, these lists store the phase 2 coordinates after n
        # moves.
        self.corner = [0] * max_length
        self.edge4 = [0] * max_length
        self.edge8 = [0] * max_length

        # the following two arrays store minimum number of moves required to
        # reach phase 2 or a solution respectively
        # after n moves. these estimates come from the pruning tables and are
        # used to exclude branches in the search tree.
        self.min_dist_1 = [0] * max_length
        self.min_dist_2 = [0] * max_length

        # initialise the arrays from the input
        self.f = FaceCube(self.facelets)
        self.c = CoordCube.from_cubiecube(self.f.to_cubiecube())
        self.twist[0] = self.c.twist
        self.flip[0] = self.c.flip
        self.udslice[0] = self.c.udslice
        self.corner[0] = self.c.corner
        self.edge4[0] = self.c.edge4
        self.edge8[0] = self.c.edge8
        self.min_dist_1[0] = self._phase_1_cost(0)

    def _phase_2_initialise(self, n):
        if time.time() > self._timeout:
            return -2
        # initialise phase 2 search from the phase 1 solution
        cc = self.f.to_cubiecube()
        for i in range(n):
            for j in range(self.power[i]):
                cc.move(self.axis[i])
        self.edge4[n] = cc.edge4
        self.edge8[n] = cc.edge8
        self.corner[n] = cc.corner
        self.min_dist_2[n] = self._phase_2_cost(n)
        for depth in range(self._allowed_length - n):
            m = self._phase_2_search(n, depth)
            if m >= 0:
                return m
        return -1

    def _phase_1_cost(self, n):
        """
        Cost of current position for use in phase 1. Returns a lower bound on
        the number of moves requires to get to phase 2.
        """
        return max(
            self.tables.udslice_twist_prune[self.udslice[n], self.twist[n]],
            self.tables.udslice_flip_prune[self.udslice[n], self.flip[n]],
        )

    def _phase_2_cost(self, n):
        """
        Cost of current position for use in phase 2. Returns a lower bound on
        the number of moves required to get to a solved cube.
        """
        return max(
            self.tables.edge4_corner_prune[self.edge4[n], self.corner[n]],
            self.tables.edge4_edge8_prune[self.edge4[n], self.edge8[n]],
        )

    def _phase_1_search(self, n, depth):
        if time.time() > self._timeout:
            return -2
        elif self.min_dist_1[n] == 0:
            return self._phase_2_initialise(n)
        elif self.min_dist_1[n] <= depth:
            for i in range(6):
                if n > 0 and self.axis[n - 1] in (i, i + 3):
                    # don't turn the same face on consecutive moves
                    # also for opposite faces, e.g. U and D, UD = DU, so we can
                    # impose that the lower index happens first.
                    continue
                for j in range(1, 4):
                    self.axis[n] = i
                    self.power[n] = j
                    mv = 3 * i + j - 1

                    # update coordinates
                    self.twist[n + 1] = self.tables.twist_move[self.twist[n]][
                        mv
                    ]
                    self.flip[n + 1] = self.tables.flip_move[self.flip[n]][mv]
                    self.udslice[n + 1] = self.tables.udslice_move[
                        self.udslice[n]
                    ][mv]
                    self.min_dist_1[n + 1] = self._phase_1_cost(n + 1)

                    # start search from next node
                    m = self._phase_1_search(n + 1, depth - 1)
                    if m >= 0:
                        return m
                    if m == -2:
                        # time limit exceeded
                        return -2
        # if no solution found at current depth, return -1
        return -1

    def _phase_2_search(self, n, depth):
        if self.min_dist_2[n] == 0:
            return n
        elif self.min_dist_2[n] <= depth:
            for i in range(6):
                if n > 0 and self.axis[n - 1] in (i, i + 3):
                    continue
                for j in range(1, 4):
                    if i in [1, 2, 4, 5] and j != 2:
                        # in phase two we only allow half turns of the faces
                        # R, F, L, B
                        continue
                    self.axis[n] = i
                    self.power[n] = j
                    mv = 3 * i + j - 1

                    # update coordinates following the move mv
                    self.edge4[n + 1] = self.tables.edge4_move[self.edge4[n]][
                        mv
                    ]
                    self.edge8[n + 1] = self.tables.edge8_move[self.edge8[n]][
                        mv
                    ]
                    self.corner[n + 1] = self.tables.corner_move[
                        self.corner[n]
                    ][mv]
                    self.min_dist_2[n + 1] = self._phase_2_cost(n + 1)

                    # start search from new node
                    m = self._phase_2_search(n + 1, depth - 1)
                    if m >= 0:
                        return m
        # if no moves lead to a tree with a solution or min_dist_2 > depth then
        # we return -1 to signify lack of solution
        return -1

    def _solution_to_string(self, length):
        """
        Generate solution string. Uses standard cube notation: F means
        clockwise quarter turn of the F face, U' means a counter clockwise
        quarter turn of the U face, R2 means a half turn of the R face etc.
        """

        def recover_move(axis_power):
            axis, power = axis_power
            if power == 1:
                return Color(axis).name
            if power == 2:
                return Color(axis).name + "2"
            if power == 3:
                return Color(axis).name + "'"
            raise RuntimeError("Invalid move in solution.")

        solution = map(
            recover_move, zip(self.axis[:length], self.power[:length])
        )
        return " ".join(solution)
        
# Read cube state from JSON
with open('Tester.json', 'r') as f:
  cube_state = json.load(f)
  
# Convert JSON to FaceCube
def json_to_facecube(cube_json):
  color_map = {'WHITE': 'U', 'RED': 'R', 'GREEN': 'F',
               'YELLOW': 'D', 'ORANGE': 'L', 'BLUE': 'B'}
  
  facelet_string = ""
  for face in ['top', 'right', 'front', 'bottom', 'left', 'back']:
    for x in range(3):
      for y in range(3):
        color = cube_json[face][f"{x},{y}"]
        facelet_string += color_map[color]
        
  return FaceCube(facelet_string)

# Solve the cube  
facecube = json_to_facecube(cube_state)
manager = SolutionManager(facecube.to_string())
solution = manager.solve()

print(f"Solution: {solution}")
