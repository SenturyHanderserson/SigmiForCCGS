import tkinter as tk
import threading
import pyautogui
import keyboard
import time

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.mode = tk.StringVar(value="click")  # possible values: "click", "space", "custom"
        self.custom_key = None  # to store the user-selected key
        self.custom_hook = None  # reference to the keyboard hook for custom key selection

        self.setup_ui()

        # Start a background thread to listen for F1 press (to Start/Stop)
        threading.Thread(target=self.listen_f1, daemon=True).start()

    def setup_ui(self):
        """Create and place all UI elements."""
        self.root.title("Auto Clicker / Spacebar / Custom Key")
        self.root.geometry("400x200")

        # Title / instruction label
        mode_label = tk.Label(self.root, text="Choose Mode:")
        mode_label.pack(pady=5)

        # Radio buttons for modes
        click_radio = tk.Radiobutton(self.root, text="Left Click", variable=self.mode, value="click")
        click_radio.pack()

        space_radio = tk.Radiobutton(self.root, text="Space Bar", variable=self.mode, value="space")
        space_radio.pack()

        custom_radio = tk.Radiobutton(self.root, text="Custom Key", variable=self.mode, value="custom")
        custom_radio.pack()

        # Button to select a custom key
        select_key_button = tk.Button(self.root, text="Select Key", command=self.select_key)
        select_key_button.pack(pady=5)

        # A label to display which key has been selected (or instructions during selection)
        self.key_info_label = tk.Label(self.root, text="No custom key selected yet.", fg="blue")
        self.key_info_label.pack(pady=5)

        # A label to show the current running/stopped status at all times
        self.run_status_label = tk.Label(self.root, text="Stopped. Press F1 to Start/Stop", fg="red")
        self.run_status_label.pack(pady=5)

    def listen_f1(self):
        """
        This method runs in a separate thread.
        It waits for the user to press F1, then toggles the running state.
        """
        while True:
            keyboard.wait("F1")  # blocks until F1 is pressed
            self.running = not self.running

            if self.running:
                self.run_status_label.config(text="Running... (Press F1 to Stop)", fg="green")
                # Start the autoclicker/keypress loop in another thread
                threading.Thread(target=self.auto_clicker, daemon=True).start()
            else:
                self.run_status_label.config(text="Stopped. Press F1 to Start", fg="red")

    def select_key(self):
        """
        Called when the user clicks "Select Key".
        We temporarily hook keyboard presses to get a single key from the user.
        """
        self.key_info_label.config(text="Press any key to select it...", fg="blue")

        # If there was an old hook, unhook it first to avoid conflicts
        if self.custom_hook is not None:
            keyboard.unhook(self.custom_hook)
            self.custom_hook = None

        def on_key_press(event):
            # When the user presses any key, store that key and unhook
            self.custom_key = event.name
            self.key_info_label.config(text=f"Selected key: {self.custom_key}", fg="blue")
            keyboard.unhook(self.custom_hook)
            self.custom_hook = None

        # Set up a new hook for a single key press
        self.custom_hook = keyboard.on_press(on_key_press)

    def auto_clicker(self):
        """
        This loop runs repeatedly while self.running is True.
        Depending on the selected mode, it either clicks the mouse or presses a key every 0.1s.
        """
        while self.running:
            mode = self.mode.get()
            if mode == "click":
                pyautogui.click()
            elif mode == "space":
                pyautogui.press("space")
            elif mode == "custom" and self.custom_key is not None:
                pyautogui.press(self.custom_key)
            time.sleep(0.1)

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
