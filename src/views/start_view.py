# src/views/start_view.py

import tkinter as tk
from tkinter import ttk


def build_start_window():
    root = tk.Tk()
    root.title("MusictoSound")
    root.state("zoomed")  # pantalla completa

    frm = ttk.Frame(root, padding=40)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        frm,
        text="MusictoSound",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(0, 20))

    ttk.Label(
        frm,
        text="Selecciona el modo de trabajo",
        font=("Segoe UI", 12)
    ).pack(pady=(0, 40))

    transcribe_btn = ttk.Button(frm, text="Transcribir partitura")
    transcribe_btn.pack(fill="x", pady=15, ipady=15)

    reaper_btn = ttk.Button(frm, text="Procesar XML por pistas")
    reaper_btn.pack(fill="x", pady=15, ipady=15)

    return {
        "root": root,
        "transcribe_btn": transcribe_btn,
        "reaper_btn": reaper_btn,
    }