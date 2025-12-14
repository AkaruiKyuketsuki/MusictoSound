# src/views/xml_viewer.py
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os
import subprocess
import platform
from tkinter import messagebox


def _open_pdf(pdf_path: Path):
    """Abre un PDF con el visor por defecto del sistema."""
    if platform.system() == "Windows":
        os.startfile(str(pdf_path))  # type: ignore
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(pdf_path)])
    else:
        subprocess.Popen(["xdg-open", str(pdf_path)])


def show_xml_score(pdf_path: Path):
    """
    Muestra una ventana para visualizar la partitura generada desde MusicXML.
    """
    win = tk.Toplevel()
    win.title("Partitura generada desde MusicXML")
    win.geometry("500x260")
    win.resizable(True, True)

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(
        frm,
        text="Se ha generado una partitura a partir del archivo MusicXML.",
        wraplength=380,
        font=("Segoe UI", 10, "bold"),
    ).pack(pady=(10, 6))

    ttk.Label(
        frm,
        text=(
            "Puedes visualizar la partitura utilizando el visor de partituras "
            "del sistema o bien abrirla directamente dentro de la aplicación."
        ),
        wraplength=380,
        justify="center",
    ).pack(pady=(0, 18))

    ttk.Button(
        frm,
        text="🎼 Abrir en visor del sistema",
        command=lambda: _open_pdf(pdf_path),
        width=30,
    ).pack(pady=6)

    def _open_in_app():
        tk.messagebox.showinfo(
            "Funcionalidad en desarrollo",
            "La visualización de la partitura dentro de la aplicación "
            "se implementará en una fase posterior."
        )

    ttk.Button(
        frm,
        text="Ver en la aplicación",
        command=_open_in_app,
        width=30,
    ).pack(pady=6)
