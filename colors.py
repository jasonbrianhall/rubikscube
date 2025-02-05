from enum import Enum

class CubeColor(Enum):
    RED = (1.0, 0.0, 0.0)
    YELLOW = (1.0, 1.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    ORANGE = (1.0, 0.5, 0.0)
    WHITE = (1.0, 1.0, 1.0)
    UNASSIGNED = (0.8, 0.8, 0.8)
    INTERIOR = (0, 0, 0)
