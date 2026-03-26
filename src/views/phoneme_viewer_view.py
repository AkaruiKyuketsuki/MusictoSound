import tkinter as tk
from tkinter import ttk


def open_phoneme_viewer(parent):

    viewer = tk.Toplevel(parent)
    viewer.title("Fonética generada")
    viewer.geometry("600x400")

    main = ttk.Frame(viewer, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Fonética generada",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", pady=(0,10))

    phoneme_box = tk.Text(main, wrap="word")
    phoneme_box.pack(fill="both", expand=True)

    phoneme_box.insert(
        "1.0",
        "Soprano:\nki.ɾje e.lej.son\n\n"
        "Alto:\nki.ɾje e.lej.son\n\n"
        "Tenor:\nki.ɾje e.lej.son\n\n"
        "Bajo:\nki.ɾje e.lej.son\n"
    )

    phoneme_box.configure(state="disabled")

    ttk.Button(
        main,
        text="Cerrar",
        command=viewer.destroy
    ).pack(pady=10)