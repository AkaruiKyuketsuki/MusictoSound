import tkinter as tk


class ReaperGuideOverlay:

    def __init__(self, root):

        self.root = root
        self.windows = []

        self.create_hint("👇 STEP 1\nCLICK 'Actions'", 400, 80)
        self.create_hint("👇 STEP 2\nCLICK 'Show action list'", 420, 120)
        self.create_hint("👉 STEP 3\nTYPE: visible", 650, 200)
        self.create_hint("⭐ STEP 4\nCLICK RUN", 650, 350)

        self.create_close_button()


    def create_hint(self, text, x, y):

        win = tk.Toplevel(self.root)

        win.overrideredirect(True)
        win.attributes("-topmost", True)

        frame = tk.Frame(
            win,
            bg="#222",
            padx=15,
            pady=10,
            bd=3,
            relief="solid"
        )

        frame.pack()

        label = tk.Label(
            frame,
            text=text,
            fg="white",
            bg="#222",
            font=("Segoe UI", 14, "bold"),
            justify="center"
        )

        label.pack()

        win.geometry(f"+{x}+{y}")

        self.windows.append(win)


    def create_close_button(self):

        win = tk.Toplevel(self.root)

        win.overrideredirect(True)
        win.attributes("-topmost", True)

        btn = tk.Button(
            win,
            text="❌ Close guide",
            font=("Segoe UI", 12, "bold"),
            bg="#cc3333",
            fg="white",
            command=self.close_all
        )

        btn.pack(padx=10, pady=5)

        win.geometry("+50+50")

        self.windows.append(win)


    def close_all(self):

        for w in self.windows:
            w.destroy()