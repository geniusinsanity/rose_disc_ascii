# Entry point to run the rose disc animation
import argparse
import os
import sys
import time
import signal

# Add parent folder so imports work when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from rose_disc_ascii.config import (
        DEFAULT_ROWS, DEFAULT_COLS, FPS, LOOP_TIME
    )
    from rose_disc_ascii.renderer import AsciiRenderer
except ImportError:
    from config import (
        DEFAULT_ROWS, DEFAULT_COLS, FPS, LOOP_TIME
    )
    from renderer import AsciiRenderer


def run_terminal(rows, cols, fps, max_frames=None):
    # Runs the animation directly in the terminal using ANSI colors
    sys.stdout.write("\033[?25l\033[2J")  # Hide cursor and clear
    sys.stdout.flush()

    def exit_cleanly(sig=None, frame=None):
        sys.stdout.write("\033[?25h\033[0m\n")  # Show cursor and reset color
        sys.stdout.flush()
        sys.exit(0)

    signal.signal(signal.SIGINT, exit_cleanly)
    signal.signal(signal.SIGTERM, exit_cleanly)

    renderer = AsciiRenderer(rows=rows, cols=cols)
    start_time = time.perf_counter()
    frame_interval = 1.0 / fps
    frame_count = 0

    try:
        while True:
            t_start = time.perf_counter()
            t = (t_start - start_time) % LOOP_TIME

            frame_str = renderer.to_ansi(t)
            sys.stdout.write(frame_str)
            sys.stdout.flush()

            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break

            elapsed = time.perf_counter() - t_start
            sleep_time = max(0.001, frame_interval - elapsed)
            time.sleep(sleep_time)

    finally:
        exit_cleanly()


def run_window(rows, cols, fps):
    # Runs the desktop window with Tkinter
    try:
        from rose_disc_ascii.gui import RoseDiscWindow
    except ImportError:
        from gui import RoseDiscWindow
    window = RoseDiscWindow(target_fps=fps, rows=rows, cols=cols)
    window.run()


def main():
    parser = argparse.ArgumentParser(
        description="Rose Disc - ASCII Animation in Python"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Run inside the terminal instead of opening a window"
    )
    parser.add_argument(
        "--fps", type=int, default=FPS,
        help=f"Target frame rate (default: {FPS})"
    )
    parser.add_argument(
        "--rows", type=int, default=DEFAULT_ROWS,
        help=f"Number of rows (default: {DEFAULT_ROWS})"
    )
    parser.add_argument(
        "--cols", type=int, default=DEFAULT_COLS,
        help=f"Number of columns (default: {DEFAULT_COLS})"
    )
    parser.add_argument(
        "--frames", type=int, default=None,
        help="Stop after this number of frames (for terminal mode)"
    )

    args = parser.parse_args()

    if args.cli:
        run_terminal(args.rows, args.cols, args.fps, max_frames=args.frames)
    else:
        run_window(args.rows, args.cols, args.fps)


if __name__ == "__main__":
    main()
