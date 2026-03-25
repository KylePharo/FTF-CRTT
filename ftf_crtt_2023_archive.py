import tkinter as tk
from tkinter import *
from tkinter import ttk
import random
import datetime
import time
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime
import csv
import os
import threading

### Experiment Configuration ###################################################
# Customise variables and text messages here, for ease of use.
################################################################################
# Number of games to play
NUM_GAMES = 3

# Default break condition for each game (must match condition_options values)
DEFAULT_GAME_CONDITIONS = ["No Break", "5 Seconds", "10 Seconds"]

# Number of rounds per game
# NUM_ROUNDS = 30
NUM_ROUNDS = 4

# Maximum number of seconds to wait during game (s)
# MAX_WAIT = 8
MAX_WAIT = 8

# Minimum number of seconds to wait during game (s)
MIN_WAIT = 0
MIN_WAIT = 0

# Set time difference to override random win (ms)
ELAPSED_TIME = 100

# Set the timeout for second player response (s)
RESPONSE_TIMEOUT = 3

# Set the keys for each player
KEY1 = "1"
KEY2 = "2"

# Window Dimensions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Set font details
FONT_TYPE = "Helvetica"
FONT_SIZE = 50
FONT_COLOUR = "white"
GO_COLOUR = "orange"
BG_COLOUR = "black"

# Provide pathname for audio file
blast_file = AudioSegment.from_mp3(
    "radio_static.mp3"
)

FILE_NAME = datetime.today().strftime('%Y%m%d%H')
save_files = []
col_names = ["win_num", "sound", "ttrs", "ttbp", "ttbi"]

default_blast_id = ""

### Text Strings ###############################################################
# Configurable text strings to be used during the experiment.
# '{}' characters can be replaced dynamically using the .format() function.
# NOTE: Editing any strings with '{}' in them MAY REQUIRE editing the .format()
# 		function where they are implemented (You can use CTRL+F to find them).
################################################################################

# game text
text_welcome = "Welcome!"
text_space_continue = "Press Space to continue"
text_p1_name = "Player 1, type name then hit Enter:"
text_p2_name = "Player 2, type name then hit Enter:"

text_keys = "{} is using the '{}' key.\n{} is using the '{}' key."
text_instructions = "When you see GO!!, hit your key before your opponent."

text_round = "Round {}"

text_get_ready = "Ready..."
text_get_set = "Set..."
text_go = "GO!!"

text_win = "{} Wins!" \
           "\n\n{}, select a blast level from 1-8" \
           "\n\n{}, standby 😈"
text_blast = "Standby for blast..."

text_win_wait = "{} wins!\n\n{}, take {} seconds and decide\n\nwhat blast level you want to set for {}"

text_valid = "That is an invalid response.\nPlease select a blast level between 1-8.\n\n{}, standby for blast level:"

text_game_complete = "Game {} complete!\n\nPress Space to begin Game {}"
text_game_over = "All games complete!\nThanks for playing!"


get_date = datetime.today().strftime('%Y%m%d')

### Setting up audio ###########################################################
# db levels will vary by computer and headphones, must be assessed for each set up
# set my computer to full volume

blast_file_1 = blast_file - 38
blast_file_2 = blast_file - 33
blast_file_3 = blast_file - 29
blast_file_4 = blast_file - 23
blast_file_5 = blast_file - 18
blast_file_6 = blast_file - 15
blast_file_7 = blast_file + 1
blast_file_8 = blast_file + 20

blast_file_l1 = blast_file_1.pan(-1)
blast_file_l2 = blast_file_2.pan(-1)
blast_file_l3 = blast_file_3.pan(-1)
blast_file_l4 = blast_file_4.pan(-1)
blast_file_l5 = blast_file_5.pan(-1)
blast_file_l6 = blast_file_6.pan(-1)
blast_file_l7 = blast_file_7.pan(-1)
blast_file_l8 = blast_file_8.pan(-1)

blast_file_r1 = blast_file_1.pan(1)
blast_file_r2 = blast_file_2.pan(1)
blast_file_r3 = blast_file_3.pan(1)
blast_file_r4 = blast_file_4.pan(1)
blast_file_r5 = blast_file_5.pan(1)
blast_file_r6 = blast_file_6.pan(1)
blast_file_r7 = blast_file_7.pan(1)
blast_file_r8 = blast_file_8.pan(1)

blast_file_1.split_to_mono()

### Setting Up GUI #############################################################
# Set up the Tkinter GUI that the players will use.
################################################################################

root = tk.Tk()
root.title("Competitive Reaction Time Game")
root.configure(bg=BG_COLOUR)
root.attributes('-fullscreen', True)

# Set the window size

# root.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT))

# Initialise global variables
player_names = {}
win_num = None
game_round = 0
game_data = {}
time_to_round_start = 0
time_to_button_press = 0
time_to_blast_initiate = 0
FORCED_BREAK_TIME = 0
TIMEOUT_COUNTER = 0
_timeout_id = None
first_presser = None
current_game_index = 0
game_condition_vars = []

display_text = tk.StringVar()
display_label = tk.Label(
    root,
    fg=FONT_COLOUR,
    bg=BG_COLOUR,
    justify="center",
    textvariable=display_text,
    font=(FONT_TYPE, FONT_SIZE)
)

entry_label = tk.Entry(
    root,
    fg=FONT_COLOUR,
    bg=BG_COLOUR,
    insertbackground=FONT_COLOUR,
    disabledbackground=BG_COLOUR,
    justify="center",
    borderwidth=0,
    highlightthickness=0,
    font=(FONT_TYPE, FONT_SIZE),
    state="disabled"
)

# Game display widgets are hidden until the settings screen is dismissed

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(2, weight=1)


### Text Functions  ############################################################
# Manipulate the text of the Label object in the window
################################################################################

# Adds text to the window, after a new line
def update_text(*new_text):
    display_text.set("".join(new_text))


def bind_keypress(func):
    root.unbind("<Return>")
    root.unbind("<space>")
    root.bind("<KeyPress>", func)


def bind_return(func):
    root.unbind("<space>")
    root.unbind("<KeyPress>")
    root.bind("<Return>", func)


def bind_space(func):
    root.unbind("<Return>")
    root.unbind("<KeyPress>")
    root.bind("<space>", func)


def flash_go():
    root.configure(bg=GO_COLOUR)
    display_label.configure(bg=GO_COLOUR)
    entry_label.configure(bg=GO_COLOUR, disabledbackground=GO_COLOUR)


def revert_flash():
    root.configure(bg=BG_COLOUR)
    display_label.configure(bg=BG_COLOUR)
    entry_label.configure(bg=BG_COLOUR, disabledbackground=BG_COLOUR)


def unbind_all():
    root.unbind("<Return>")
    root.unbind("<space>")
    root.unbind("<KeyPress>")


def allow_typing():
    entry_label.configure(state="normal")
    entry_label.focus_set()


def disable_typing():
    entry_label.configure(state="disabled")
    root.focus_set()


def clear_entry():
    entry_label.configure(state="normal")
    entry_label.delete(0, 'end')
    entry_label.configure(state="disabled")


### Settings for game ##########################################################
# These allow the experimenter to set up the game
################################################################################
condition_options = [
    "No Break",
    "5 Seconds",
    "10 Seconds",
    "15 Seconds"
]


### Stage Functions ############################################################
# These control the flow of the experiment
################################################################################
def update_settings():
    global NUM_GAMES, NUM_ROUNDS, MAX_WAIT, MIN_WAIT, RESPONSE_TIMEOUT, current_game_index
    settings_frame.grid_forget()
    display_label.grid(row=1, column=1)
    entry_label.grid(row=2, column=1)

    NUM_GAMES = num_games_var.get()
    NUM_ROUNDS = num_rounds_var.get()
    MAX_WAIT = max_wait_var.get()
    MIN_WAIT = min_wait_var.get()
    RESPONSE_TIMEOUT = timeout_var.get()
    current_game_index = 0

    start_game()

def start_game():
    update_text(text_welcome,
                "\n\n",
                text_space_continue)
    bind_space(ask_player_1)


# Function that sets the key for player 1
def ask_player_1(e):
    update_text(text_p1_name)
    bind_return(set_player_1)
    allow_typing()


def set_player_1(e):
    global player_names
    disable_typing()
    player_names[1] = entry_label.get()
    clear_entry()
    ask_player_2()


def ask_player_2():
    update_text(text_p2_name)
    bind_return(set_player_2)
    allow_typing()


def set_player_2(e):
    global player_names
    disable_typing()
    player_names[2] = entry_label.get()
    clear_entry()
    start_next_game()


def start_next_game(e=None):
    global FORCED_BREAK_TIME, game_round, game_data, save_files, current_game_index

    game_round = 0
    game_data = {}
    save_files = []

    condition_str = game_condition_vars[current_game_index].get()
    if condition_str == "No Break":
        FORCED_BREAK_TIME = 0
    elif condition_str == "5 Seconds":
        FORCED_BREAK_TIME = 5
    elif condition_str == "10 Seconds":
        FORCED_BREAK_TIME = 10
    elif condition_str == "15 Seconds":
        FORCED_BREAK_TIME = 15
    else:
        FORCED_BREAK_TIME = 0

    if current_game_index == 0:
        update_text("\n\n", text_instructions, "\n\n", text_space_continue)
    else:
        update_text(f"Game {current_game_index + 1} of {NUM_GAMES}\n\n", text_space_continue)
    bind_space(check_game)


def check_game(e=None):
    global game_round
    game_round += 1

    if game_round > NUM_ROUNDS:
        end_game()

    else:
        update_text(text_round.format(game_round),
                    "\n\n",
                    text_get_ready
                    )
        bind_space(get_ready(e))


def get_ready(e):
    bind_return(start_round(e))


# Starts the game when the Space Bar is pressed.
def start_round(e):
    global time_to_round_start
    # Unbind <KeyPress> so that pressing a key won't do anything
    unbind_all()
    update_text(text_round.format(game_round), "\n\n", text_get_ready)
    end_ttrs = time.time()
    time_to_round_start = end_ttrs - begin
    print("ttsr", time_to_round_start)

    # Print "Get Set..." after 1 second (1000ms)
    root.after(1000, lambda: update_text(text_round.format(game_round), "\n\n", text_get_set))

    # Call the 'start_timer' function after a randomised delay (in Milliseconds)
    random_delay = 1000 + random.randint(MIN_WAIT, MAX_WAIT) * 1000
    root.after(random_delay, start_timer)


# Flash screen orange and record pressed keys
def start_timer():
    global time_to_button_press
    update_text("")
    flash_go()
    end_ttbp = time.time()
    time_to_button_press = end_ttbp - begin
    print("ttbp", time_to_button_press)
    bind_keypress(record_game)


# Check keypresses to see if one of them was a player.
# If yes, initiate the next stage.
def record_game(e):
    global KEY1, KEY2, game_data, game_round, win_num, t1, first_presser, _timeout_id

    if e.keysym not in (KEY1, KEY2):
        return

    if e.keysym == KEY1:
        first_presser = 1
        now = datetime.now()
        t1 = int(now.strftime("%H%M%S%f")[:-3])
        print(t1)
        print("t1")
    elif e.keysym == KEY2:
        first_presser = 2
        now = datetime.now()
        t1 = int(now.strftime("%H%M%S%f")[:-3])
        print(t1)
        print("t1")
    else:
        win_num = random.randint(1, 2)

    unbind_all()

    if FORCED_BREAK_TIME == 0:
        bind_keypress(time_check)
        print("time checking fb")
    else:
        bind_keypress(time_check_fb)
        print("time checking control")

    _timeout_id = root.after(RESPONSE_TIMEOUT * 1000, handle_timeout)


def handle_timeout():
    global win_num, _timeout_id
    _timeout_id = None
    revert_flash()
    unbind_all()
    win_num = first_presser
    if FORCED_BREAK_TIME == 0:
        root.after(10, ask_blast)
    else:
        update_text(text_win_wait.format(
            player_names[win_num], player_names[win_num],
            FORCED_BREAK_TIME, player_names[3 - win_num]))
        root.after(100, forced_break)


def time_check_fb(b):
    global KEY1, KEY2, game_data, game_round, win_num, _timeout_id

    if b.keysym not in (KEY1, KEY2):
        return

    first_presser_key = KEY1 if first_presser == 1 else KEY2
    if b.keysym == first_presser_key:
        return

    if _timeout_id is not None:
        root.after_cancel(_timeout_id)
        _timeout_id = None
    revert_flash()

    if b.keysym == KEY1:
        now = datetime.now()
        t2 = int(now.strftime("%H%M%S%f")[:-3])
        print(t2)
        print("t2")
        elapsed = int(t2) - int(t1)
        if elapsed > ELAPSED_TIME:
            win_num = 2
            print(elapsed)
            print("play 1 was sooo slow")
        else:
            print(elapsed)
            print("close enough")
            win_num = random.randint(1, 2)
    elif b.keysym == KEY2:
        now = datetime.now()
        t2 = int(now.strftime("%H%M%S%f")[:-3])
        print(t2)
        print("t2")
        elapsed = int(t2) - int(t1)
        if elapsed > ELAPSED_TIME:
            win_num = 1
            print(elapsed)
            print("play 2 was sooo slow")
        else:
            print(elapsed)
            print("close enough")
            win_num = random.randint(1, 2)
    else:
        win_num = random.randint(1, 2)
        print("error")

    unbind_all()

    update_text(text_win_wait.format(player_names[win_num], player_names[win_num], FORCED_BREAK_TIME,
                                     player_names[3 - win_num]))

    root.after(100, forced_break)


def time_check(b):
    global KEY1, KEY2, game_data, game_round, win_num, _timeout_id

    if b.keysym not in (KEY1, KEY2):
        return

    first_presser_key = KEY1 if first_presser == 1 else KEY2
    if b.keysym == first_presser_key:
        return

    if _timeout_id is not None:
        root.after_cancel(_timeout_id)
        _timeout_id = None
    revert_flash()

    if b.keysym == KEY1:
        now = datetime.now()
        t2 = int(now.strftime("%H%M%S%f")[:-3])
        print(t2)
        print("t2")
        elapsed = int(t2) - int(t1)
        if elapsed > ELAPSED_TIME:
            win_num = 2
            print(elapsed)
            print("play 1 was sooo slow")
        else:
            print(elapsed)
            print("close enough")
            win_num = random.randint(1, 2)
    elif b.keysym == KEY2:
        now = datetime.now()
        t2 = int(now.strftime("%H%M%S%f")[:-3])
        print(t2)
        print("t2")
        elapsed = int(t2) - int(t1)
        if elapsed > ELAPSED_TIME:
            win_num = 1
            print(elapsed)
            print("play 2 was sooo slow")
        else:
            print(elapsed)
            print("close enough")
            win_num = random.randint(1, 2)
    else:
        win_num = random.randint(1, 2)
        print("error")

    unbind_all()
    root.after(10, ask_blast)


# Declare the winner, and get the level of the blast
def forced_break():
    global win_num
    root.after(FORCED_BREAK_TIME*1000, ask_blast)


def ask_blast():
    global win_num, default_blast_id
    update_text(text_win.format(player_names[win_num], player_names[win_num], player_names[3 - win_num]))
    allow_typing()
    bind_keypress(validate_blast)


def validate_blast(self):
    global win_num

    if entry_label.get() in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        set_blast()
    else:
        update_text(text_valid.format(player_names[3 - win_num]))
        clear_entry()
        allow_typing()


def set_blast():
    global game_data, game_round, win_num, player_names, time_to_button_press, time_to_blast_initiate, default_blast_id
    disable_typing()
    blast_level = entry_label.get()
    end_ttbi = time.time()
    time_to_blast_initiate = end_ttbi - begin
    print("ttbi", time_to_blast_initiate)

    clear_entry()
    unbind_all()
    activate_blast(blast_level)


def activate_blast(blast_level):
    global game_data, game_round, win_num, player_names, time_to_button_press, time_to_blast_initiate, time_to_round_start

    blast_files_l = {
        "1": blast_file_l1, "2": blast_file_l2, "3": blast_file_l3, "4": blast_file_l4,
        "5": blast_file_l5, "6": blast_file_l6, "7": blast_file_l7, "8": blast_file_l8
    }
    blast_files_r = {
        "1": blast_file_r1, "2": blast_file_r2, "3": blast_file_r3, "4": blast_file_r4,
        "5": blast_file_r5, "6": blast_file_r6, "7": blast_file_r7, "8": blast_file_r8
    }

    if win_num == 1:
        audio = blast_files_l.get(blast_level, blast_file_l4)
    else:
        audio = blast_files_r.get(blast_level, blast_file_r4)

    save_files.append([win_num, blast_level, time_to_round_start, time_to_button_press, time_to_blast_initiate])

    game_data[game_round] = {
        "a": win_num,
        "a": blast_level,
        "a": time_to_round_start,
        "a": time_to_button_press,
        "a": time_to_blast_initiate
    }

    game_data[game_round]["blast_level"] = blast_level

    def play_then_continue():
        play(audio)
        root.after(0, check_game)

    threading.Thread(target=play_then_continue, daemon=True).start()


def restart_game(*_):
    global game_round, game_data, save_files, player_names, current_game_index
    game_round = 0
    game_data = {}
    save_files = []
    player_names = {}
    current_game_index = 0
    unbind_all()
    display_label.grid_remove()
    entry_label.grid_remove()
    settings_frame.grid(row=1, column=1, rowspan=2)


def _save_game_csv():
    game_number = current_game_index + 1
    fb_map = {0: "control", 5: "fb5", 10: "fb10", 15: "fb15"}
    CONDITION = fb_map.get(FORCED_BREAK_TIME, "control")
    GAME = f"game{game_number}"

    print(game_data)
    print("----------")
    print(game_data.items())
    print(get_date)

    os.makedirs(f"csv_output/{GAME}_{CONDITION}", exist_ok=True)
    with open(f"csv_output/{GAME}_{CONDITION}/{FILE_NAME}.csv", "w", newline='') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=',')
        datawriter.writerow(col_names)
        for row in save_files:
            datawriter.writerow(row)


# Print end text and unbind KeyPress.
# ==> Add any post-game functionality here.
def end_game():
    global current_game_index
    _save_game_csv()
    current_game_index += 1

    if current_game_index < NUM_GAMES:
        update_text(text_game_complete.format(current_game_index, current_game_index + 1))
        bind_space(start_next_game)
    else:
        update_text(text_game_over + "\n\nPress Enter to return to settings")
        bind_return(restart_game)


### Start Program ##############################################################
# Run calls to set the script running
################################################################################
begin = time.time()

num_games_var = tk.IntVar(value=NUM_GAMES)
num_rounds_var = tk.IntVar(value=NUM_ROUNDS)
max_wait_var = tk.IntVar(value=MAX_WAIT)
min_wait_var = tk.IntVar(value=MIN_WAIT)

# ttk style for spinboxes
_lf = (FONT_TYPE, 20)
_wf = (FONT_TYPE, 20)

style = ttk.Style()
style.theme_use('clam')
style.configure('Dark.TSpinbox',
                fieldbackground='#222222', background='#333333',
                foreground='white', arrowcolor='white',
                bordercolor='#555555', darkcolor='#222222',
                lightcolor='#222222', insertcolor='white')


class DarkDropdown(tk.Frame):
    """Custom dark-themed dropdown — replaces ttk.Combobox to avoid OS-native popup styling."""

    def __init__(self, parent, variable, values, width=14):
        super().__init__(parent, bg='#222222', cursor='hand2')
        self._var = variable
        self._values = values
        self._width = width
        self._popup = None
        self._lb = None

        self._label = tk.Label(self, textvariable=variable,
                               fg='white', bg='#222222',
                               font=_wf, width=width, anchor='w',
                               padx=10, pady=6)
        self._label.pack(side='left', fill='both', expand=True)

        self._arrow = tk.Label(self, text='▾', fg='white', bg='#3a3a3a',
                               font=(FONT_TYPE, 16), padx=8, pady=6)
        self._arrow.pack(side='right')

        for w in (self, self._label, self._arrow):
            w.bind('<Button-1>', self._toggle)

    def _toggle(self, *_):
        if self._popup and self._popup.winfo_exists():
            self._close()
        else:
            self._open()

    def _open(self):
        self.update_idletasks()
        # Coordinates relative to root so the Frame sits inside root's canvas
        x = self.winfo_rootx() - root.winfo_rootx()
        y = self.winfo_rooty() - root.winfo_rooty() + self.winfo_height()
        w = self.winfo_width()
        row_h = self.winfo_height()
        h = len(self._values) * row_h

        # Plain tk.Frame on root — no OS window, so no rounded corners
        self._popup = tk.Frame(root, bg='#222222',
                               highlightthickness=1,
                               highlightbackground='#555555')
        self._popup.place(x=x, y=y, width=w, height=h)
        self._popup.lift()

        self._lb = tk.Listbox(
            self._popup,
            fg='white', bg='#222222',
            selectbackground='#555555', selectforeground='white',
            font=_wf, bd=0, highlightthickness=0,
            activestyle='none', relief='flat'
        )
        self._lb.pack(fill='both', expand=True)

        for v in self._values:
            self._lb.insert('end', '  ' + v)

        try:
            idx = self._values.index(self._var.get())
            self._lb.selection_set(idx)
        except ValueError:
            pass

        self._lb.bind('<ButtonRelease-1>', self._select)
        self._lb.bind('<FocusOut>', lambda _: self._close())
        self._lb.focus_set()

    def _select(self, *_):
        idx = self._lb.curselection()
        if idx:
            self._var.set(self._values[idx[0]])
        self._close()

    def _close(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.place_forget()
            self._popup.destroy()
        self._popup = None

# Settings panel
settings_frame = tk.Frame(root, bg=BG_COLOUR)
settings_frame.grid(row=1, column=1, rowspan=2)

tk.Label(
    settings_frame, text="Experiment Settings",
    fg=FONT_COLOUR, bg=BG_COLOUR,
    font=(FONT_TYPE, 36, "bold")
).grid(row=0, column=0, columnspan=2, pady=(0, 30))

def _row(label, widget, r):
    tk.Label(settings_frame, text=label, fg=FONT_COLOUR, bg=BG_COLOUR,
             font=_lf, anchor="e").grid(row=r, column=0, sticky="e",
                                        padx=(0, 16), pady=8)
    widget.grid(row=r, column=1, sticky="w", pady=8)

num_games_spin = ttk.Spinbox(settings_frame, from_=1, to=10,
                              textvariable=num_games_var,
                              style='Dark.TSpinbox', font=_wf, width=6)
_row("Number of Games:", num_games_spin, 1)

game_rows_frame = tk.Frame(settings_frame, bg=BG_COLOUR)
game_rows_frame.grid(row=2, column=0, columnspan=2, pady=4)


def build_game_rows():
    global game_condition_vars
    # focus root first to close any open dropdown popup
    root.focus_set()
    for w in game_rows_frame.winfo_children():
        w.destroy()
    game_condition_vars = []
    n = num_games_var.get()
    for i in range(n):
        default = DEFAULT_GAME_CONDITIONS[i] if i < len(DEFAULT_GAME_CONDITIONS) else "No Break"
        var = tk.StringVar(value=default)
        game_condition_vars.append(var)
        tk.Label(game_rows_frame, text=f"Game {i + 1} Break:",
                 fg=FONT_COLOUR, bg=BG_COLOUR,
                 font=_lf, anchor="e"
                 ).grid(row=i, column=0, sticky="e", padx=(0, 16), pady=6)
        DarkDropdown(game_rows_frame, var, condition_options, width=14).grid(
            row=i, column=1, sticky="w", pady=6)


num_games_var.trace_add("write", lambda *_: build_game_rows())
build_game_rows()

num_rounds_spin = ttk.Spinbox(settings_frame, from_=1, to=100,
                               textvariable=num_rounds_var,
                               style='Dark.TSpinbox', font=_wf, width=6)
_row("Rounds per Game:", num_rounds_spin, 3)

max_wait_spin = ttk.Spinbox(settings_frame, from_=0, to=60,
                             textvariable=max_wait_var,
                             style='Dark.TSpinbox', font=_wf, width=6)
_row("Max Wait (s):", max_wait_spin, 4)

min_wait_spin = ttk.Spinbox(settings_frame, from_=0, to=60,
                             textvariable=min_wait_var,
                             style='Dark.TSpinbox', font=_wf, width=6)
_row("Min Wait (s):", min_wait_spin, 5)

timeout_var = tk.IntVar(value=RESPONSE_TIMEOUT)
timeout_spin = ttk.Spinbox(settings_frame, from_=1, to=30,
                            textvariable=timeout_var,
                            style='Dark.TSpinbox', font=_wf, width=6)
_row("Response Timeout (s):", timeout_spin, 6)

# tk.Label used as button — reliably respects bg/fg on all platforms
button = tk.Label(settings_frame, text="Start Game",
                  fg='white', bg='#c95000',
                  font=(FONT_TYPE, 24, "bold"),
                  padx=30, pady=12, cursor="hand2")
button.bind("<Button-1>", lambda _: update_settings())
button.grid(row=7, column=0, columnspan=2, pady=(30, 0))


root.mainloop()
