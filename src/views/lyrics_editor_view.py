import tkinter as tk
from tkinter import ttk

from services.coral_parser_service import extract_syllables_by_part

def open_lyrics_editor(parent, xml_path):

    editor = tk.Toplevel(parent)
    editor.title("Editor de letra")
    editor.geometry("900x600")

    main = ttk.Frame(editor, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Editor de letra",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0,10))

    ttk.Label(
        main,
        text=f"Archivo: {xml_path.name}",
        foreground="gray"
    ).pack(anchor="w", pady=(0,20))

    # ===============================
    # Pestañas de voces
    # ===============================

    notebook = ttk.Notebook(main)
    notebook.pack(fill="both", expand=True)

    # ===============================
    # Cargar sílabas
    # ===============================

    syllables_by_part = extract_syllables_by_part(xml_path)

    for part_name, syllables in syllables_by_part.items():

        # Crear pestaña
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=part_name)

        canvas = tk.Canvas(tab)
        canvas.configure(highlightthickness=0)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )

        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===============================
        # Frame de sílabas
        # ===============================

        part_frame = ttk.Frame(scroll_frame, padding=10)
        part_frame.pack(fill="x", pady=10)

        syllables_per_row = 12
        row = None

        for i, syl in enumerate(syllables):

            if i % syllables_per_row == 0:
                row = ttk.Frame(part_frame)
                row.pack(anchor="w", pady=2)

            lbl = ttk.Label(
                row,
                text=syl,
                relief="solid",
                padding=5
            )

            lbl.pack(side="left", padx=2)
              

    # ===============================
    # Botones inferiores
    # ===============================

    buttons = ttk.Frame(main)
    buttons.pack(fill="x", pady=10)

    ttk.Button(
        buttons,
        text="Cerrar",
        command=editor.destroy
    ).pack(side="right")
