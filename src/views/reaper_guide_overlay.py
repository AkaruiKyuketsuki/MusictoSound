import tkinter as tk


class ReaperGuideOverlay:

    def __init__(self, root):

        self.root = root
        self.windows = []

        # posiciones ajustadas
        self.create_hint("👇 STEP 1\nCLICK 'Actions'", 260, 90)#200, 60

        self.create_hint("👇 STEP 2\nCLICK 'Show action list'",260, 175)#200, 145

        self.create_hint("👉 STEP 3\nSEARCH IN FILTER\n_RSreaper_visible_lyrics", 260, 320) #920, 220

        self.create_hint("⭐ STEP 4\nCLICK RUN", 260, 420)#920, 420

        self.create_close_button()


    def create_hint(self, text, x, y):

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)

        frame = tk.Frame(
            win,
            bg="#222",
            padx=18,
            pady=12,
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
            font=("Segoe UI", 13, "bold"),
            bg="#cc3333",
            fg="white",
            padx=20,
            pady=6,
            command=self.close_all
        )

        btn.pack()

        # posición inferior centrada
        #win.geometry("+850+700")
        win.geometry("+260+550")


        self.windows.append(win)


    def close_all(self):

        for w in self.windows:
            w.destroy()