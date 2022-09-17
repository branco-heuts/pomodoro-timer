import sys
from os import path
from tkinter import Tk, Canvas, PhotoImage, Label
from tkinter_custom_button import TkinterCustomButton
from playsound import playsound
from colour import Color
from math import floor

# Pomodoro timing
WORK_MIN = 25  # Default = 25min
SHORT_BREAK_MIN = 5  # Default = 5min
LONG_BREAK_MIN = 30  # Default = 30min

# Aesthetics GUI
YELLOW = "#FFEEAD"
GREEN = "#96CEB4"
PINK = "#D9534F"
RED = "#e7305b"
ORANGE = "FFAD60"
FONT_NAME = "Courier"

# Color gradient
NEUTRAL_BG_COLOR = Color('#ffeead')
END_WORK_BG_COLOR = Color('#ffad60')
START_BREAK_BG_COLOR = Color('#CFEFFF')


def resource_path(relative_path):
    """ Get absolute path to resource, retrieves files for PyInstaller-created .exe"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


res_path = resource_path("static/")

PICTURES = [
    res_path + "tomato5.png",
    res_path + "tomato1.png",
    res_path + "tomato2.png",
    res_path + "tomato3.png",
    res_path + "tomato4.png"
]
SOUND = res_path + "sound_effect.mp3"


class App(Tk):
    def __init__(self):
        super().__init__()

        # Parameters
        self.color_index = 0
        self.current_image_index = 0
        self.button_state = 1  # ON
        self.cycles = 0
        self.pomodoros = 0
        self.timer = None
        self.work_sec = WORK_MIN * 60
        self.short_break_sec = SHORT_BREAK_MIN * 60
        self.long_break_sec = LONG_BREAK_MIN * 60

        # GUI
        self.title("Pomodoro Timer")
        self.config(padx=5, pady=25, bg=YELLOW)
        self.grid_columnconfigure(1, minsize=210)
        self.resizable(False, False)
        self.wm_attributes("-topmost", "False")
        self.wm_attributes("-toolwindow", "True")

        # Canvas
        self.canvas = Canvas(width=350, height=224, bg=YELLOW, highlightthickness=0)
        self.canvas.grid(column=1, row=1)
        self.images = [
            PhotoImage(file=PICTURES[0]),
            PhotoImage(file=PICTURES[1]),
            PhotoImage(file=PICTURES[2]),
            PhotoImage(file=PICTURES[3]),
            PhotoImage(file=PICTURES[4])]
        self.image_id = self.canvas.create_image(175, 85, image=self.images[self.current_image_index])

        # Mechanics
        def start_button():
            """
            Button mechanics: On / Off
            """
            if self.button_state == 1:  # ON
                start_timer()
                self.button_state *= -1
            else:  # OFF
                self.start_button.set_text(text="    Start    ")
                reset_timer()
                self.button_state *= -1

        def change_image():
            """
            Change tomato image according to pomodoro cycles.
            """
            self.current_image_index += 1
            if self.current_image_index == len(self.images):  # Reset image cycle
                self.current_image_index = 0
            self.canvas.itemconfig(self.image_id, image=self.images[self.current_image_index])

        def change_background_color(background=None):
            """
            Change background colors to color index (per second).
            """
            self.config(bg=background[self.color_index])
            self.canvas.config(bg=background[self.color_index])
            self.label_timer.config(bg=background[self.color_index])
            self.start_button.configure_color(bg_color=background[self.color_index])

        def start_timer():
            """
            Timer mechanics:
                - Work for 25min
                - Short break (default=5min)
                - After 4 cycles, take a long break (default=30min)
            """
            self.cycles += 1
            self.color_index = 0

            # Set countdown times
            if self.cycles % 8 == 0:  # Long break
                self.label_timer.config(text="Break", fg=RED)
                count_down(self.long_break_sec)
            elif self.cycles % 2 == 0:  # Short break
                self.label_timer.config(text="Break", fg=PINK)
                count_down(self.short_break_sec)
            else:
                self.label_timer.config(text="Work", fg=GREEN)
                count_down(self.work_sec)

            # Change background image every pomodoro cycle
            if (self.cycles - 1) == 0 and self.pomodoros == 0:  # Change image when pressing start
                change_image()
            if (self.cycles - 1) % 2 == 0 and self.cycles >= 2:  # Add Tomato every Pomodoro
                change_image()
                self.pomodoros += 1
            if self.cycles == 9:  # Reset
                reset_timer()
                self.button_state *= -1

        def play_sound(seconds=None):
            """
            Play sound at end of each cycle.
            """
            if seconds + 1 == self.color_index:
                playsound(SOUND)
                self.wm_attributes("-topmost", "True")

        def count_down(count):
            """
            Countdown mechanics. Updates clock, changes background color (gradient), plays sounds at the end of each
            cycle.
            :param count: Seconds for each cycle
            """
            count_min = floor(count / 60)
            count_sec = count % 60

            # Adds str(0) when timer reaches single digits
            if len(str(count_sec)) == 1:
                count_sec = "0" + str(count_sec)
            if len(str(count_min)) == 1:
                count_min = "0" + str(count_min)

            # Update background color and play sound every cycle
            if self.cycles % 8 == 0:  # Long break
                change_background_color(list(START_BREAK_BG_COLOR.range_to(NEUTRAL_BG_COLOR, self.long_break_sec + 1)))
                self.color_index += 1
                self.start_button.set_text(text="    Stop    ")
                play_sound(self.long_break_sec)
                self.wm_attributes("-topmost", "False")
            elif self.cycles % 2 == 0:  # Short break
                change_background_color(list(START_BREAK_BG_COLOR.range_to(NEUTRAL_BG_COLOR, self.short_break_sec + 1)))
                self.color_index += 1
                self.start_button.set_text(text="    Stop    ")
                play_sound(self.short_break_sec)
                self.wm_attributes("-topmost", "False")
            else:
                change_background_color(list(NEUTRAL_BG_COLOR.range_to(END_WORK_BG_COLOR, self.work_sec + 1)))
                self.color_index += 1
                self.start_button.set_text(text="    Stop    ")
                play_sound(self.work_sec)
                self.wm_attributes("-topmost", "False")

            # Countdown
            self.canvas.itemconfig(self.timer_text, text=f"{count_min}:{count_sec}")
            if count > 0:
                self.timer = self.after(1000, count_down, count - 1)
            else:
                start_timer()

        def reset_timer():
            """
            Resets counts, labels, and background color/image
            """
            # Reset count
            self.cycles = 0
            self.pomodoros = 0

            # Reset label
            self.label_timer.config(text="Timer", fg=GREEN)
            self.after_cancel(self.timer)
            self.canvas.itemconfig(self.timer_text, text="00:00")

            # Reset background colors
            self.color_index = 0
            change_background_color(list(NEUTRAL_BG_COLOR.range_to(END_WORK_BG_COLOR, self.long_break_sec + 1)))

            # Reset background image
            self.current_image_index = -1
            change_image()

        # Initialize timer
        self.timer_text = self.canvas.create_text(177, 198, text="00:00", fill=GREEN, font=(FONT_NAME, 35, "bold"))
        self.label_timer = Label(text="Timer", fg=GREEN, font=(FONT_NAME, 50, "bold"), bg=YELLOW)
        self.label_timer.grid(column=1, row=0)
        self.start_button = TkinterCustomButton(text="   Start   ", corner_radius=10, command=start_button)
        self.start_button.grid(column=1, row=4)

        self.mainloop()


if __name__ == "__main__":
    App()
