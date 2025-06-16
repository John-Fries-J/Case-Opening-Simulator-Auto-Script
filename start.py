import asyncio
import platform
import pyautogui
from PIL import ImageGrab
import keyboard
import tkinter as tk
from tkinter import ttk
import threading

FPS = 60

class ColorCheckerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Color Checker")
        self.root.geometry("300x330")
        
        self.colors = {
            "Yellow/Gold": [(255, 255, 0), (255, 215, 0)],
            "Blue": [(85, 111, 242)],
            "Pink": [(204, 59, 220)],
            "Purple": [(138, 81, 242)],
            "Red": [(255, 0, 0)]
        }
        
        self.check_x, self.check_y = 956, 349
        self.reroll_x, self.reroll_y = 996, 380
        self.sell_x, self.sell_y = 913, 389
        
        self.color_vars = {}
        self.hotkey = "h"
        self.hotkey_label = None
        self.create_gui()
        
        self.running = False

    def create_gui(self):
        tk.Label(self.root, text="Select colors you want to keep:").pack(pady=5)
        for color_name in self.colors:
            var = tk.BooleanVar(value=True if color_name == "Yellow/Gold" else False)
            self.color_vars[color_name] = var
            tk.Checkbutton(self.root, text=color_name, variable=var).pack(anchor="w", padx=10)
        
        tk.Label(self.root, text="Stop hotkey:").pack(pady=5)
        self.hotkey_label = tk.Label(self.root, text=f"Current: {self.hotkey}")
        self.hotkey_label.pack(pady=5)
        tk.Button(self.root, text="Set Hotkey", command=self.set_hotkey).pack(pady=5)
        
        self.start_button = tk.Button(self.root, text="Start", command=self.toggle_script)
        self.start_button.pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=5)

    def set_hotkey(self):
        self.hotkey_label.config(text="Press any key...")
        self.root.update()
        key = keyboard.read_key(suppress=True)
        self.hotkey = key
        self.hotkey_label.config(text=f"Current: {self.hotkey}")
        print(f"Hotkey set to: {self.hotkey}")

    def get_pixel_color(self, x, y):
        screenshot = ImageGrab.grab().load()
        return screenshot[x, y]

    def is_close_to_color(self, target_color, pixel_color, tolerance=50):
        return all(abs(a - b) <= tolerance for a, b in zip(target_color, pixel_color))

    def check_selected_colors(self, pixel_color):
        for color_name, color_values in self.colors.items():
            if self.color_vars[color_name].get():
                for target_color in color_values:
                    if self.is_close_to_color(target_color, pixel_color):
                        return color_name, True
        return None, False

    def update_loop(self):
        current_color = self.get_pixel_color(self.check_x, self.check_y)
        color_name, match_found = self.check_selected_colors(current_color)
        
        if match_found:
            print(f"{color_name} detected, reroll triggered")
            pyautogui.click(self.reroll_x, self.reroll_y)
        else:
            print("Selling triggered")
            pyautogui.click(self.sell_x, self.sell_y)

    async def main_loop(self):
        print(f"Press '{self.hotkey}' to stop the script. Running...")
        print(f"Checking color at ({self.check_x}, {self.check_y})")
        
        while self.running and not keyboard.is_pressed(self.hotkey):
            self.update_loop()
            await asyncio.sleep(1.0 / FPS)
        
        self.running = False
        self.start_button.config(text="Start")
        self.status_label.config(text="Status: Stopped")
        print("Script stopped")

    def toggle_script(self):
        if not self.running:
            if not any(var.get() for var in self.color_vars.values()):
                self.status_label.config(text="Select at least one color!")
                return
            self.running = True
            self.start_button.config(text="Stop")
            self.status_label.config(text=f"Status: Running (Stop: '{self.hotkey}')")
            threading.Thread(target=lambda: asyncio.run(self.main_loop()), daemon=True).start()
        else:
            self.running = False

    def run(self):
        self.root.mainloop()

if platform.system() == "Emscripten":
    app = ColorCheckerApp()
    asyncio.ensure_future(app.main_loop())
else:
    if __name__ == "__main__":
        app = ColorCheckerApp()
        app.run()