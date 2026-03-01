import tkinter as tk
from tkinter import ttk


def build_reaper_window():
    root = tk.Tk()
    root.title("MusictoSound - Reaper XML")
    root.state("zoomed")

    frm = ttk.Frame(root, padding=40)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        frm,
        text="Procesamiento XML para Reaper",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(0, 30))

    ttk.Label(
        frm,
        text="Esta funcionalidad se implementará próximamente.",
        font=("Segoe UI", 11)
    ).pack(pady=(0, 40))

    back_btn = ttk.Button(frm, text="Volver")

    back_btn.pack(pady=20)

    return {
        "root": root,
        "back_btn": back_btn,
    }