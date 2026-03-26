import tkinter as tk
from tkinter import ttk


def open_lyrics_editor(parent):

    editor = tk.Toplevel(parent)
    editor.title("Editor de letra")
    editor.geometry("700x500")

    main = ttk.Frame(editor, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Editar letra",
        font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", pady=(0,10))

    text_box = tk.Text(main, wrap="word")
    text_box.pack(fill="both", expand=True)

    text_box.insert("1.0", "Soprano:\n\nAlto:\n\nTenor:\n\nBajo:\n")

    buttons = ttk.Frame(main)
    buttons.pack(fill="x", pady=10)

    ttk.Button(
        buttons,
        text="Guardar"
    ).pack(side="right", padx=5)

    ttk.Button(
        buttons,
        text="Cerrar",
        command=editor.destroy
    ).pack(side="right")