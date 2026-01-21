# src/controllers/gui_controller.py
import threading
import os
import subprocess
import platform
from pathlib import Path

from views.gui_view import build_window
from models.models import ConversionRequest, ConversionMode
from services.conversion_service import convert_score

from services.xml_render_service import render_xml_to_pdf
from views.xml_viewer import show_xml_score

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
def _run_conversion(log, request: ConversionRequest, root, progress, start_btn, auto_open_var, on_view_xml, on_edit,):
    try:
        log("▶ Iniciando conversión... (ESTE PROCESO PODRÍA TARDAR UNOS MINUTOS)")
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

            if auto_open_var.get():
                log("🔁 Apertura automática activada")
                root.after(0, on_view_xml)
                root.after(0, on_edit)

        else:
            log("❌ Error durante la conversión")
            log(result.message)

    except Exception as e:
        log(f"❌ Excepción inesperada: {e}")
    
    finally:
        log("— Fin del proceso —")
        
        def finish():
            progress.stop()
            progress.pack_forget()
            start_btn.config(state="normal")

        root.after(0, finish)

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
    view_xml_btn = widgets["view_xml_btn"]
    edit_btn = widgets["edit_btn"]
    progress = widgets["progress"]
    auto_open_var = widgets["auto_open_var"]

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

        progress.pack(pady=6)
        progress.start(10)   # velocidad de animación
        start_btn.config(state="disabled")


        # Lanzar conversión en hilo
        thread = threading.Thread(
            target=_run_conversion,
            args=(log, request, root, progress, start_btn, auto_open_var, on_view_xml, on_edit,),
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
    def on_view_xml():
        outdir = Path(outdir_var.get().strip() or "output")

        if not outdir.exists():
            log(f"⚠ La carpeta de salida no existe: {outdir}")
            return

        xml_files = list(outdir.glob("*.xml")) + list(outdir.glob("*.mxl"))

        if not xml_files:
            log("⚠ No se ha encontrado ningún archivo MusicXML para visualizar")
            return

        # Elegir el archivo más reciente (última transcripción)
        xml_path = max(xml_files, key=lambda p: p.stat().st_mtime)

        log(f"🎼 Generando partitura desde: {xml_path.name}")

        try:
            pdf_path = render_xml_to_pdf(xml_path, outdir)
            log(f"✅ Partitura generada correctamente: {pdf_path.name}")

            #show_xml_score(pdf_path)
            original_pdf = Path(infile_var.get())
            show_xml_score(original_pdf, pdf_path)

        except Exception as e:
            log(f"❌ Error al visualizar la partitura: {e}")

    # ------------------------------------------------------
    def on_edit():
        outdir = Path(outdir_var.get().strip() or "output")

        if not outdir.exists():
            log(f"⚠ La carpeta de salida no existe: {outdir}")
            return

        # Solo buscamos archivos editables
        xml_files = list(outdir.glob("*.mxl")) + list(outdir.glob("*.xml"))

        if not xml_files:
            log("⚠ No se ha encontrado ningún archivo MusicXML para editar")
            return

        # Usar el más reciente
        xml_path = max(xml_files, key=lambda p: p.stat().st_mtime)

        try:
            _open_with_default_app(xml_path)
            log(f"🎵 Abriendo partitura para edición: {xml_path.name}")
        except Exception as e:
            log(f"❌ No se pudo abrir el editor: {e}")

    # ------------------------------------------------------
    start_btn.config(command=on_start)
    open_btn.config(command=on_open_output)
    view_xml_btn.config(command=on_view_xml)
    edit_btn.config(command=on_edit)

    root.mainloop()
