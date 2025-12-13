# src/controllers/gui_controller.py  (Tkinter Controller)
import os
import subprocess
import platform
from pathlib import Path

from views.gui_view import build_window

def _open_with_default_app(path: Path):
    """Open file or folder with OS default application."""
    if platform.system() == "Windows":
        os.startfile(str(path))     # type: ignore
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])

def run_gui():
    """Launch the GUI. Buttons do not run conversion yet."""
    widgets = build_window()

    root = widgets["root"]
    log = widgets["log"]
    infile_var = widgets["infile_var"]
    outdir_var = widgets["outdir_var"]
    mode_var = widgets["mode_var"]
    start_btn = widgets["start_btn"]
    open_btn = widgets["open_btn"]

    log("Interfaz gráfica lista. Aún sin lógica conectada.")

    def on_start():
        infile = infile_var.get().strip()
        outdir = outdir_var.get().strip() or "output"
        mode = mode_var.get()
        log(f"[INFO] Iniciar pulsado")
        log(f"Archivo: {infile or '(no seleccionado)'}")
        log(f"Salida: {outdir}")
        log(f"Modo: {mode}")
        log("⚠ Aún no conectado a la lógica de conversión.")

    def on_open():
        outdir = outdir_var.get().strip() or "output"
        p = Path(outdir)
        if not p.exists():
            log(f"[ERROR] La carpeta no existe: {p}")
            return
        try:
            _open_with_default_app(p)
            log(f"Abrir carpeta: {p}")
        except Exception as e:
            log(f"[ERROR] No se pudo abrir la carpeta: {e}")

    start_btn.config(command=on_start)
    open_btn.config(command=on_open)

    root.mainloop()
