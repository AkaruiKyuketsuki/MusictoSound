import tkinter as tk
from tkinter import ttk
from pathlib import Path

#from services.coral_parser_service import extract_phonemes_by_part
from services.phoneme_service import extract_phonemes_by_part

def open_phoneme_viewer(parent, xml_path, language):

    viewer = tk.Toplevel(parent)
    viewer.title("Fonética generada")
    viewer.geometry("900x600")

    main = ttk.Frame(viewer, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Fonética generada",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0,10))

    ttk.Label(
        main,
        text=f"Idioma: {language}",
        foreground="gray"
    ).pack(anchor="w", pady=(0,15))

    # ===============================
    # Pestañas por voz
    # ===============================

    notebook = ttk.Notebook(main)
    notebook.pack(fill="both", expand=True)

    phonemes_by_part = extract_phonemes_by_part(xml_path, language)

    for part_name, pairs in phonemes_by_part.items():

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

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===============================
        # Contenido fonético
        # ===============================

        part_frame = ttk.Frame(scroll_frame, padding=10)
        part_frame.pack(fill="x", pady=10)

        per_row = 8
        row = None

        for i, (syl, phon) in enumerate(pairs):

            if i % per_row == 0:
                row = ttk.Frame(part_frame)
                row.pack(anchor="w", pady=5)

            cell = ttk.Frame(row)
            cell.pack(side="left", padx=5)

            # Sílabas (arriba)
            ttk.Label(
                cell,
                text=syl,
                font=("Segoe UI", 10, "bold")
            ).pack()

            # Fonética (abajo)
            ttk.Label(
                cell,
                text=phon,
                foreground="blue"
            ).pack()

    # ===============================
    # Botón cerrar
    # ===============================

    ttk.Button(
        main,
        text="Cerrar",
        command=viewer.destroy
    ).pack(pady=10)