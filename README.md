# Star Catcher

A simple 2D arcade game built with Python and Pygame. Move a basket left and right to catch falling stars, avoid bombs, and beat your high score.

## Requirements

- **Python 3.8 or newer** ([python.org/downloads](https://www.python.org/downloads/))
- **Pygame 2.5+** (installed automatically from `requirements.txt`)

The game has no image or sound files — only `game.py` is needed to play.

## Setup on another computer

### 1. Copy the project

Choose one of these options:

**Option A — Git (if you use GitHub)**

```bash
git clone https://github.com/francomlawa/StarCatcherGame.git
cd StarCatcherGame
```

**Option B — Manual copy**

Copy the whole project folder to the other computer (at minimum you need `game.py` and `requirements.txt`).

### 2. Create a virtual environment (recommended)

Using a virtual environment keeps Pygame isolated from the rest of your system.

**Linux / macOS**

```bash
cd path/to/gameken
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (Command Prompt or PowerShell)**

```cmd
cd path\to\gameken
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the game

With the virtual environment activated:

```bash
python game.py
```

On some Linux systems you may need `python3` instead of `python`:

```bash
python3 game.py
```

The game starts in **fullscreen**. Press **ESC** to quit.

### Alternative: install without a virtual environment

If you prefer not to use a venv:

```bash
pip install pygame
python game.py
```

On Linux, if `pip` reports a “externally managed environment” error, use a virtual environment (step 2 above) instead of `--break-system-packages`.

## How to play

- Move the basket with the **LEFT** and **RIGHT** arrow keys.
- Catch **yellow stars** (+1 point) and **golden stars** (+5 points).
- Build **combos** by catching stars without missing — higher combos give bonus points.
- Grab **cyan shields** for one free bomb block.
- Avoid **red bombs**. Catching a bomb costs a life unless you have a shield.
- Missing stars also costs a life. Difficulty increases as your score grows.

### Controls

| Key | Action |
|-----|--------|
| LEFT / RIGHT | Move the basket |
| R | Restart after game over |
| ESC | Quit the game |

## Files created at runtime

The game saves your best score to `highscore.txt` in the same folder as `game.py`. You do not need to create this file yourself.

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `ModuleNotFoundError: No module named 'pygame'` | Activate the venv, then run `pip install -r requirements.txt` |
| `python: command not found` | Use `python3 game.py` |
| Game window is blank or crashes | Update graphics drivers; try another Python version (3.10–3.12) |
| Cannot exit fullscreen | Press **ESC** |
| Permission errors on Linux | Run from a folder where you can write files (for `highscore.txt`) |

## Project structure

```
gameken/
├── game.py           # Main game
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── highscore.txt     # Created automatically (optional to copy)
```
