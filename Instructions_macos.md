# macOS Setup Instructions

These instructions walk you through running the FTF-CRTT on a clean macOS machine.

## Prerequisites

You will need:
- The script you want to run (e.g. `ftf_crtt_2023_archive.py`)
- The audio file `radio_static.mp3` in the same folder as the script

---

## Step 1: Install Homebrew

Homebrew is a package manager for macOS that we use to install system dependencies.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen prompts. It will ask for your password. After installation, Homebrew may ask you to run a few commands to add it to your PATH — do those before continuing.

---

## Step 2: Install System Dependencies

Python with Tkinter support, PortAudio (required for audio playback), and ffmpeg (required for MP3 decoding):

```bash
brew install python-tk portaudio ffmpeg
```

This may take several minutes on a fresh machine.

---

## Step 3: Navigate to the Project Folder

Open Terminal and change directory to wherever you saved the script and audio file. For example, if they are in your Downloads folder:

```bash
cd ~/Downloads
```

---

## Step 4: Create and Activate a Virtual Environment

Use the Homebrew-managed Python explicitly to ensure tkinter support is included:

```bash
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
```

Your terminal prompt should now show `(.venv)` at the start, indicating the virtual environment is active.

> **Note:** Using `/opt/homebrew/bin/python3` instead of just `python3` is important if you have a Python version manager like pyenv installed. Those Python builds often lack tkinter support, causing the script to fail at launch.

---

## Step 5: Install Python Packages

```bash
pip install -r requirements_desktop.txt
```

If you do not have the requirements file, install the packages manually:

```bash
pip install "pydub==0.25.1" "PyAudio==0.2.14"
```

> **Note:** PyAudio requires PortAudio to be installed first (Step 2). If you skipped that step and see a build error mentioning `portaudio.h`, go back and run `brew install portaudio`, then retry.

---

## Step 6: Run the Script

```bash
python3 ftf_crtt_2023_archive.py
```

A fullscreen game window should open. Press `Ctrl+C` in the terminal or close the window to exit.

---

## Step 7: Deactivate the Virtual Environment (when done)

```bash
deactivate
```

---

## Returning to the Project Later

You do not need to repeat Steps 1–3 on future sessions. Just activate the environment and run:

```bash
cd ~/Downloads          # or wherever your project folder is
source .venv/bin/activate
python3 ftf_crtt_2023_archive.py
```

---

## Troubleshooting

**`portaudio.h` file not found when installing PyAudio**
PortAudio is not installed. Run `brew install portaudio` and then retry `pip install PyAudio`.

**`No module named 'tkinter'` or `cannot import name '_tkinter'`**
Your Python was not built with tkinter support. This commonly happens when using pyenv. Fix it by recreating the virtual environment with the Homebrew Python:
```bash
rm -rf .venv
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_desktop.txt
```
If `brew install python-tk` has not been run yet, do that first.

**Audio plays out of both headphones instead of just one**
macOS may be mirroring mono audio to both channels. Go to System Settings > Sound and check for audio enhancement or spatial audio settings and disable them.

**`No module named 'audioop'` or `No module named 'pyaudioop'`**
The `audioop` module was removed in Python 3.13+. The `audioop-lts` package in `requirements_desktop.txt` provides it as a backport. If you installed packages manually without the requirements file, run:
```bash
pip install audioop-lts
```

**`JSONDecodeError` when loading audio / ffprobe crashes with `Library not loaded: libvpx`**
Your Homebrew ffmpeg installation is broken due to a dependency update. Reinstall it:
```bash
brew reinstall ffmpeg
```

**The script cannot find `radio_static.mp3`**
The audio file must be in the same folder as the `.py` script. Check that both files are in the same directory before running.
