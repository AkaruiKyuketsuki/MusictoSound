# src/controllers/gui_controller.py
import threading
import os
import subprocess
import platform
from pathlib import Path

from views.gui_view import build_window
from models.models import ConversionRequest, ConversionMode
from services.conversion_service import convert_score


# ==========================================================
# Utilidades
# ==========================================================
def _open_with_default_app(path: Path):
    if platform.system() == "Windows":
        os.startfile(str(path))  # type: ignore
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


# ==========================================================
# Worker (hilo de conversión)
# ==========================================================
def _run_conversion(log, request: ConversionRequest):
    try:
        log("▶ Iniciando conversión...")
        log(f"  Entrada: {request.input_path}")
        log(f"  Salida:  {request.output_dir}")
        log(f"  Modo:    {request.mode.name}")

        result = convert_score(request)

        if result.success:
            log("✅ Conversión finalizada correctamente")
            log(result.message)

            if result.output_file:
                log(f"📄 Archivo generado: {result.output_file}")
                try:
                    _open_with_default_app(Path(result.output_file))
                    log("📂 Archivo abierto con la aplicación por defecto")
                except Exception as e:
                    log(f"⚠ No se pudo abrir automáticamente: {e}")
        else:
            log("❌ Error durante la conversión")
            log(result.message)

    except Exception as e:
        log(f"❌ Excepción inesperada: {e}")

    log("— Fin del proceso —")


# ==========================================================
# Controlador principal GUI
# ==========================================================
def run_gui():
    widgets = build_window()

    root = widgets["root"]
    log = widgets["log"]
    infile_var = widgets["infile_var"]
    outdir_var = widgets["outdir_var"]
    mode_var = widgets["mode_var"]
    start_btn = widgets["start_btn"]
    open_btn = widgets["open_btn"]

    log("Interfaz gráfica lista.")

    # ------------------------------------------------------
    def on_start():
        infile = infile_var.get().strip()
        outdir = outdir_var.get().strip() or "output"
        mode_str = mode_var.get()

        if not infile:
            log("⚠ Selecciona un archivo de entrada")
            return

        input_path = Path(infile)
        if not input_path.is_file():
            log(f"❌ El archivo no existe: {input_path}")
            return

        output_dir = Path(outdir)
        output_dir.mkdir(parents=True, exist_ok=True)

        mode = (
            ConversionMode.FULL_AUTOMATIC
            if mode_str == "auto"
            else ConversionMode.MANUAL_ASSISTED
        )

        request = ConversionRequest(
            input_path=input_path,
            output_dir=output_dir,
            mode=mode,
        )

        log("===================================")
        log("🟢 Botón INICIAR pulsado")
        log(f"Modo seleccionado: {mode.name}")

        # Lanzar conversión en hilo
        thread = threading.Thread(
            target=_run_conversion,
            args=(log, request),
            daemon=True,
        )
        thread.start()

    # ------------------------------------------------------
    def on_open_output():
        outdir = outdir_var.get().strip() or "output"
        path = Path(outdir)
        if not path.exists():
            log(f"⚠ La carpeta no existe: {path}")
            return
        try:
            _open_with_default_app(path)
            log(f"📂 Carpeta abierta: {path}")
        except Exception as e:
            log(f"❌ No se pudo abrir la carpeta: {e}")

    # ------------------------------------------------------
    start_btn.config(command=on_start)
    open_btn.config(command=on_open_output)

    root.mainloop()
