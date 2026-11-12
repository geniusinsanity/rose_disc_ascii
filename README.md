# Rose Disc - ASCII Animation

This project is an ASCII art animation in Python based on the reference video of a CD jewel case with a spinning disc and a red rose inside.

The whole animation is drawn using text characters and colors. It calculates the shapes and lighting with math (NumPy) and draws them into a grid of characters, with no images or video files used.

## Features

- **Procedural ASCII Graphics:** The case borders, corners, rotating disc, concentric grooves, and rose flower are all computed mathematically with code.
- **Smaller Font / Higher Resolution:** Uses a small font size (size 7 by default, 64 rows by 128 columns) so the text is dense and smooth, showing fine petal curves and reflections clearly.
- **Tkinter Desktop Window:** Draws the animation in a window and only updates the characters that actually change each frame, which keeps it running smoothly at 30-60 FPS without high CPU usage.
- **Terminal Mode:** Can also run directly inside your Linux or Windows terminal with 24-bit ANSI colors using the `--cli` flag.
- **Seamless Loop:** One full rotation takes 18.572 seconds and loops continuously without jumping.

## Controls

- `Space`: Pause or resume the animation
- `R`: Restart animation from the beginning
- `F` or `F11`: Toggle fullscreen
- `Esc`: Exit fullscreen, or close the window
- `Q`: Quit

## How to Install and Run

### 1. Requirements

You only need Python 3.9+ and NumPy (Tkinter comes with standard Python):

```bash
pip install -r requirements.txt
```

### 2. Run the Window

```bash
python3 main.py
```

### 3. Run in the Terminal

```bash
python3 main.py --cli
```

You can also pass custom size and speed:
```bash
python3 main.py --fps 60 --rows 64 --cols 128
```

## How to Build Standalone Executables

### Linux (Kali Linux / Ubuntu / Debian)

You can build a single binary file that runs without needing Python installed on the target machine:

```bash
./build_linux.sh
```

The output file will be created at:
```bash
./dist/rose_disc
```

To run it:
```bash
./dist/rose_disc
```

### Windows (.exe)

#### Method 1: GitHub Actions (Automatic)
The repository contains `.github/workflows/build-windows.yml`. When you push to GitHub, the workflow automatically runs on a Windows machine, builds `rose_disc.exe`, and gives you the download link under the Actions tab.

#### Method 2: Build Manually on Windows
On a Windows machine with Python installed:

```powershell
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --noconfirm rose_disc.spec
```

The executable will be in `dist\rose_disc.exe`.

## Project Structure

- `config.py`: Settings, colors, character ramp, and object dimensions.
- `procedural.py`: Math formulas for the case, disc, and rose petals.
- `renderer.py`: Converts the math values into character brightness and ANSI strings.
- `gui.py`: Tkinter window and efficient screen update logic.
- `main.py`: Main entry point (CLI and GUI arguments).
- `build_linux.sh`: Shell script to create the Linux binary with PyInstaller.
- `rose_disc.spec`: PyInstaller configuration file.
- `.github/workflows/build-windows.yml`: GitHub Actions workflow for Windows builds.
