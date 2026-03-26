# src/views/reaper_export_view.py
import tkinter as tk
from tkinter import ttk


def show_reaper_export_dialog(parent):
    """
    Muestra un diálogo para seleccionar opciones de exportación a Reaper.
    Devuelve un diccionario con las opciones seleccionadas o None si se cancela.
    """

    result = {"value": None}

    win = tk.Toplevel(parent)
    win.title("Exportar a Reaper")
    win.geometry("420x320")

    # Centrar ventana si la principal está maximizada
    parent.update_idletasks()

    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()

    win_width = 420
    win_height = 365

    x = parent_x + (parent_width // 2) - (win_width // 2)
    y = parent_y + (parent_height // 2) - (win_height // 2)

    win.geometry(f"{win_width}x{win_height}+{x}+{y}")


    win.resizable(False, False)

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(
        frm,
        text="Opciones de exportación a Reaper",
        font=("Segoe UI", 11, "bold")
    ).pack(pady=(10, 15))

    # ======================================================
    # Formato de exportación
    # ======================================================

    format_frame = ttk.LabelFrame(frm, text="Formato", padding=10)
    format_frame.pack(fill="x", pady=5)

    #format_var = tk.StringVar(value="midi_wav")
    format_var = tk.StringVar(value="both")

    ttk.Radiobutton(
        format_frame,
        text="MIDI",
        variable=format_var,
        value="midi"
    ).pack(anchor="w")

    ttk.Radiobutton(
        format_frame,
        text="WAV",
        variable=format_var,
        value="wav"
    ).pack(anchor="w")

    ttk.Radiobutton(
        format_frame,
        text="MIDI + WAV",
        variable=format_var,
        #value="midi_wav"
        value="both"
    ).pack(anchor="w")

    # ======================================================
    # Opciones adicionales
    # ======================================================

    options_frame = ttk.LabelFrame(frm, text="Opciones", padding=10)
    options_frame.pack(fill="x", pady=10)

    tempo_var = tk.BooleanVar(value=True)
    transpose_var = tk.BooleanVar(value=True)
    lyrics_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(
        options_frame,
        text="Aplicar tempo final",
        variable=tempo_var
    ).pack(anchor="w")

    ttk.Checkbutton(
        options_frame,
        text="Aplicar transposición global",
        variable=transpose_var
    ).pack(anchor="w")

    """
    ttk.Checkbutton(
        options_frame,
        text="Incluir tutorial para añadir letra",
        variable=lyrics_var
    ).pack(anchor="w")
    """

    lyrics_check = ttk.Checkbutton(
        options_frame,
        text="Incluir tutorial para añadir letra",
        variable=lyrics_var
    )

    lyrics_check.pack(anchor="w")

    def update_lyrics_state(*args):

        if format_var.get() == "wav":

            lyrics_check.state(["disabled"])
            lyrics_var.set(False)

        else:

            lyrics_check.state(["!disabled"])

    format_var.trace_add("write", update_lyrics_state)
    update_lyrics_state()
    
    # ======================================================
    # Botones
    # ======================================================

    buttons = ttk.Frame(frm)
    buttons.pack(pady=15)

    def on_export():

        result["value"] = {
            "format": format_var.get(),
            "apply_tempo": tempo_var.get(),
            "apply_transpose": transpose_var.get(),
            "include_lyrics": lyrics_var.get(),
        }

        win.destroy()

    def on_cancel():
        win.destroy()

    ttk.Button(
        buttons,
        text="Exportar",
        command=on_export,
        width=15
    ).pack(side="left", padx=10)

    ttk.Button(
        buttons,
        text="Cancelar",
        command=on_cancel,
        width=15
    ).pack(side="left", padx=10)

    win.grab_set()
    parent.wait_window(win)

    return result["value"]