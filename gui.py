# Desktop window for the animation using Tkinter
import time
import tkinter as tk
import tkinter.font as tkf
import numpy as np

from .config import (
    LOOP_TIME, FPS, UPDATE_BUDGET,
    DEFAULT_ROWS, DEFAULT_COLS, ASCII_CHARS, COLOR_LEVELS, FONT_SIZE
)
from .renderer import AsciiRenderer


class RoseDiscWindow:
    def __init__(self, target_fps=FPS, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
        self.target_fps = target_fps
        self.rows = rows
        self.cols = cols
        self.paused = False
        self.fullscreen = False
        self.font_size = FONT_SIZE
        self.renderer = AsciiRenderer(rows=self.rows, cols=self.cols)

        # Create window
        self.root = tk.Tk()
        self.root.title("Rose Disc - ASCII Animation")
        self.root.configure(bg="#010203")

        # Pick a good monospace font available on this system
        fonts = set(tkf.families())
        self.font_name = next(
            (f for f in ("Cascadia Mono", "Consolas", "DejaVu Sans Mono", "Courier New", "Courier")
             if f in fonts), "Courier"
        )
        self.load_font()

        # Canvas for drawing the text
        self.canvas_w = int(self.cols * self.char_w)
        self.canvas_h = int(self.rows * self.char_h)

        # Center window on screen
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        pos_x = max(0, (scr_w - self.canvas_w) // 2)
        pos_y = max(0, (scr_h - self.canvas_h) // 2 - 25)
        self.root.geometry(f"{self.canvas_w}x{self.canvas_h}+{pos_x}+{pos_y}")

        self.canvas = tk.Canvas(
            self.root, width=self.canvas_w, height=self.canvas_h,
            bg="#010203", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Tracking arrays so we only update characters that changed
        self.items = np.zeros((self.rows, self.cols), dtype=object)
        self.items[:] = 0
        self.last_char = np.zeros((self.rows, self.cols), dtype=np.int32)
        self.last_color = np.zeros((self.rows, self.cols, 3), dtype=np.int16)

        # Cache for hex color strings
        self.color_cache = {}

        # Timing and speed tracking
        self.start_time = time.perf_counter()
        self.pause_time = 0.0
        self.update_budget = UPDATE_BUDGET
        self.char_cost = 0.008

        self.bind_keys()

    def load_font(self):
        # Setup font and measure character size
        self.font = tkf.Font(root=self.root, family=self.font_name, size=self.font_size, weight="bold")
        self.char_w = self.font.measure("M")
        self.char_h = self.font.metrics("linespace")

    def bind_keys(self):
        # Connect keyboard buttons
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<F>", self.toggle_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.handle_escape)
        self.root.bind("<q>", lambda e: self.root.destroy())
        self.root.bind("<Q>", lambda e: self.root.destroy())

    def toggle_pause(self, event=None):
        if not self.paused:
            self.paused = True
            self.pause_time = time.perf_counter()
        else:
            self.paused = False
            # Resume without skipping time
            self.start_time += (time.perf_counter() - self.pause_time)

    def restart(self, event=None):
        self.start_time = time.perf_counter()
        if self.paused:
            self.pause_time = self.start_time

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def handle_escape(self, event=None):
        if self.fullscreen:
            self.toggle_fullscreen()
        else:
            self.root.destroy()

    def get_hex_color(self, rgb):
        # Convert quantized RGB values to a hex string like #ff0044
        key = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        hex_val = self.color_cache.get(key)
        if hex_val is None:
            max_lvl = COLOR_LEVELS - 1
            r = key[0] * 255 // max_lvl
            g = key[1] * 255 // max_lvl
            b = key[2] * 255 // max_lvl
            hex_val = f"#{r:02x}{g:02x}{b:02x}"
            self.color_cache[key] = hex_val
        return hex_val

    def find_changes(self, char_idx, colors):
        # Checks which cells changed character or color
        char_changed = (char_idx != self.last_char)
        color_diff = np.abs(colors - self.last_color).max(axis=2)
        both_empty = (char_idx == 0) & (self.last_char == 0)

        need_draw = (~both_empty) & (char_changed | (color_diff >= 1))
        changed_cells = np.flatnonzero(need_draw)

        # Keep frame rate steady if too many characters changed at once
        if len(changed_cells) > self.update_budget:
            priority = (char_changed.astype(np.int16) * 6 + color_diff).ravel()[changed_cells]
            top_indices = np.argpartition(-priority, self.update_budget)[:self.update_budget]
            changed_cells = changed_cells[top_indices]

        return changed_cells

    def tick(self):
        # Main update loop called every frame
        t_start = time.perf_counter()

        if not self.paused:
            current_t = t_start - self.start_time
        else:
            current_t = self.pause_time - self.start_time

        # Loop the animation continuously
        t = current_t % LOOP_TIME

        # 1. Render new frame data
        char_idx, colors, _ = self.renderer.render_frame(t)

        # 2. Find which cells need updating
        update_list = self.find_changes(char_idx, colors)

        # 3. Update canvas text items
        t_draw_start = time.perf_counter()
        cw = self.char_w
        ch = self.char_h
        cols = self.cols

        for cell_idx in update_list:
            r, c = divmod(int(cell_idx), cols)
            letter = ASCII_CHARS[char_idx[r, c]]
            fill = self.get_hex_color(colors[r, c])
            item = self.items[r, c]

            if item == 0:
                if letter == ' ':
                    self.last_char[r, c] = 0
                    self.last_color[r, c] = colors[r, c]
                    continue
                # Create text object if not created yet
                self.items[r, c] = self.canvas.create_text(
                    (c + 0.5) * cw, (r + 0.5) * ch,
                    text=letter, fill=fill,
                    font=self.font, anchor="center"
                )
            else:
                self.canvas.itemconfig(item, text=letter, fill=fill)

            self.last_char[r, c] = char_idx[r, c]
            self.last_color[r, c] = colors[r, c]

        # 4. Adjust budget dynamically based on machine speed
        num_drawn = len(update_list)
        if num_drawn > 80:
            time_per_char = (time.perf_counter() - t_draw_start) / num_drawn
            self.char_cost = 0.75 * self.char_cost + 0.25 * time_per_char
            target_draw_time = 0.015  # aim for ~15ms per frame update
            self.update_budget = int(min(14000, max(800, target_draw_time / max(self.char_cost, 1e-6))))

        # 5. Schedule the next frame
        elapsed = (time.perf_counter() - t_start) * 1000.0
        frame_time = 1000.0 / self.target_fps
        wait_ms = max(1, int(frame_time - elapsed))
        self.root.after(wait_ms, self.tick)

    def run(self):
        self.root.after(50, self.tick)
        self.root.mainloop()
