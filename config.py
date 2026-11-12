# Configuration settings for the rose disc animation
import numpy as np

# Animation settings
LOOP_TIME = 18.572              # Time for one full rotation in seconds
ROT_SPEED = -2.0 * np.pi / LOOP_TIME  # Clockwise rotation speed (rad/sec)
FPS = 30                        # Target frames per second
UPDATE_BUDGET = 4500            # Max characters to update per frame for smooth speed

# Character grid size
DEFAULT_ROWS = 64               # Number of rows (smaller font allows more rows)
DEFAULT_COLS = 128              # Number of columns
FONT_SIZE = 7                   # Small font size for higher detail and smoothness
SUPER_SAMPLE = 2                # 2x2 sampling per character to make edges smooth
CHAR_ASPECT = 1.95              # Height to width ratio of monospace characters

# ASCII character ramp from dark to bright
ASCII_CHARS = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
NUM_CHARS = len(ASCII_CHARS) - 1

# Color levels for cache
COLOR_LEVELS = 28

# Case dimensions (normalized from -1.0 to 1.0)
CASE_SIZE = 0.82                # Half size of the square case
CORNER_RADIUS = 0.08            # Rounded corner radius
WALL_THICKNESS = 0.038          # Thickness of the plastic border
INNER_TRAY_RADIUS = 0.745       # Circular tray line inside the case

# Left latch tab dimensions
LATCH_LEFT = -0.92
LATCH_RIGHT = -0.76
LATCH_BOTTOM = -0.22
LATCH_TOP = 0.22

# CD disc dimensions
DISC_RADIUS = 0.718             # Outer disc radius
HOLE_RADIUS = 0.108             # Center hole radius
CLAMP_RADIUS = 0.185            # Center plastic clamp radius
PIN_DISTANCE = 0.146            # Distance of the 4 small holes from center
PIN_RADIUS = 0.016              # Radius of the small holes
STEP_RADIUS = 0.252             # Plastic step ring radius
GROOVE_START = 0.260            # Where data grooves start
GROOVE_END = 0.705              # Where data grooves end

# Rose dimensions
ROSE_RADIUS = 0.58

# Colors (RGB values from 0.0 to 1.0)
BG_COLOR = np.array([0.004, 0.007, 0.012], dtype=np.float32)
CASE_RIM_COLOR = np.array([0.90, 0.95, 1.00], dtype=np.float32)
ACRYLIC_COLOR = np.array([0.08, 0.12, 0.16], dtype=np.float32)
DISC_EDGE_COLOR = np.array([0.75, 0.88, 0.98], dtype=np.float32)
DISC_SURFACE_COLOR = np.array([0.04, 0.06, 0.09], dtype=np.float32)

# Red colors for the rose petals
ROSE_RED = np.array([0.72, 0.05, 0.16], dtype=np.float32)       # Normal red
ROSE_DARK = np.array([0.22, 0.01, 0.04], dtype=np.float32)      # Shadow between petals
ROSE_LIGHT = np.array([0.98, 0.32, 0.44], dtype=np.float32)     # Highlights on petal edges
