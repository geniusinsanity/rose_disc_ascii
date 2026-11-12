# Converts the math scene into an ASCII character grid
import numpy as np
from .config import (
    ASCII_CHARS, NUM_CHARS, COLOR_LEVELS,
    SUPER_SAMPLE, CHAR_ASPECT, DEFAULT_ROWS, DEFAULT_COLS
)
from .procedural import draw_scene


class AsciiRenderer:
    def __init__(self, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, supersample=SUPER_SAMPLE, char_aspect=CHAR_ASPECT):
        self.rows = rows
        self.cols = cols
        self.supersample = supersample
        self.char_aspect = char_aspect
        self.setup_grid()

    def set_size(self, rows, cols):
        # Change grid dimensions and recreate coordinates
        if rows != self.rows or cols != self.cols:
            self.rows = rows
            self.cols = cols
            self.setup_grid()

    def setup_grid(self):
        # Create x and y coordinate grids with supersampling
        sub_h = self.rows * self.supersample
        sub_w = self.cols * self.supersample

        # Adjust for character width/height ratio so circle stays round
        vis_w = self.cols / self.char_aspect
        vis_h = float(self.rows)

        max_side = max(vis_w, vis_h)
        scale_x = (vis_w / max_side) * 1.05
        scale_y = (vis_h / max_side) * 1.05

        ys = np.linspace(-scale_y, scale_y, sub_h, dtype=np.float32)
        xs = np.linspace(-scale_x, scale_x, sub_w, dtype=np.float32)
        self.grid_x, self.grid_y = np.meshgrid(xs, ys)

    def render_frame(self, t):
        # 1. Calculate image with 2x2 samples per character
        high_res = draw_scene(self.grid_x, self.grid_y, t)

        # 2. Average the sub-pixels into single character cells
        ss = self.supersample
        cells = high_res.reshape(self.rows, ss, self.cols, ss, 3).mean(axis=(1, 3))

        # 3. Calculate brightness from RGB
        brightness = 0.299 * cells[..., 0] + 0.587 * cells[..., 1] + 0.114 * cells[..., 2]

        # 4. Curve the brightness slightly so dark red petals show nice texture
        curved = np.clip(brightness, 0.0, 1.0) ** 0.78
        char_idx = np.clip(curved * NUM_CHARS, 0, NUM_CHARS).astype(np.int32)

        # 5. Quantize colors so we can cache hex strings
        quant_colors = np.clip((cells * (COLOR_LEVELS - 1)).astype(np.int16), 0, COLOR_LEVELS - 1)

        return char_idx, quant_colors, cells

    def to_ansi(self, t):
        # Formats the frame with 24-bit ANSI colors for terminal display
        char_idx, _, raw_cells = self.render_frame(t)
        rgb_vals = np.clip(raw_cells * 255.0, 0, 255).astype(np.uint8)

        output_lines = []
        for r in range(self.rows):
            line = []
            last_color = None
            for c in range(self.cols):
                idx = char_idx[r, c]
                ch = ASCII_CHARS[idx]
                if ch == ' ':
                    line.append(' ')
                    continue

                color = (rgb_vals[r, c, 0], rgb_vals[r, c, 1], rgb_vals[r, c, 2])
                if color != last_color:
                    line.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")
                    last_color = color
                line.append(ch)
            output_lines.append("".join(line))

        return "\033[H" + "\n".join(output_lines) + "\033[0m"
