# src/controllers/gui_controller.py
import threading
import os
import subprocess
import platform
from pathlib import Path
from tkinter import filedialog

from views.gui_view import build_window
from models.models import ConversionRequest, ConversionMode
from services.conversion_service import convert_score

from services.xml_render_service import render_xml_to_pdf
from views.xml_viewer import show_xml_score

from views.start_view import build_start_window
from views.coral_view import build_coral_view_window

from services.coral_parser_service import analyze_coral_parts
from services.coral_midi_service import export_selected_parts_to_midi

from services.coral_midi_service import export_mix_to_midi
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
# Controlador principal GUI, con selección de modo
# ==========================================================
def run_gui():

    widgets = build_start_window()

    root = widgets["root"]
    transcribe_btn = widgets["transcribe_btn"]
    reaper_btn = widgets["reaper_btn"]

    def open_transcription():
        root.destroy()
        run_transcription_gui()

    def open_coral():
        root.destroy()
        run_coral_gui()

    transcribe_btn.config(command=open_transcription)
    reaper_btn.config(command=open_coral)

    root.mainloop()


# ==========================================================
# Controlador de la vista Coral
# ==========================================================
def run_coral_gui():

    widgets = build_coral_view_window()

    root = widgets["root"]
    xml_path_var = widgets["xml_path_var"]
    browse_btn = widgets["browse_btn"]
    analyze_btn = widgets["analyze_btn"]
    back_btn = widgets["back_btn"]
    log = widgets["log"]

    set_voices = widgets["set_voices"]
    view_score_btn = widgets["view_score_btn"]
    generate_btn = widgets["generate_btn"]
    get_selected_voices = widgets["get_selected_voices"]
  
    folder_name_var = widgets["folder_name_var"]
    base_path_var = widgets["base_path_var"]
    browse_base_btn = widgets["browse_base_btn"]

    download_wav_btn = widgets["download_wav_btn"]
    get_mix_levels = widgets["get_mix_levels"]
    download_mix_btn = widgets["download_mix_btn"]
    
    log("Módulo generador coral listo.")

    # ------------------------------------------------------
    # Volver
    # ------------------------------------------------------
    def go_back():
        root.destroy()
        run_gui()

    # ------------------------------------------------------
    # Visualizar partitura
    # ------------------------------------------------------
    def on_view_score():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        path = Path(xml_path)

        if not path.is_file():
            log(f"❌ El archivo no existe: {path}")
            return

        log("Generando partitura visual...")

        try:
            output_dir = path.parent
            pdf_path = render_xml_to_pdf(path, output_dir)

            log(f"✅ Partitura generada correctamente: {pdf_path.name}")

            # Mostrar PDF generado
            show_xml_score(None, pdf_path)

        except Exception as e:
            log(f"❌ Error al visualizar la partitura: {e}")

    # ------------------------------------------------------
    # Examinar XML
    # ------------------------------------------------------
    def browse_xml():
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            filetypes=[("MusicXML files", "*.xml *.mxl"), ("All files", "*.*")]
        )

        if path:
            xml_path_var.set(path)

            # 🔹 Limpiar voces anteriores
            clear_detected_voices()

            log(f"Archivo seleccionado: {path}")

    # ------------------------------------------------------
    # Analizar voces
    # ------------------------------------------------------
    def analyze():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        path = Path(xml_path)

        if not path.is_file():
            log(f"❌ El archivo no existe: {path}")
            return

        log("Analizando archivo XML...")

        try:
            result = analyze_coral_parts(path)
        except Exception as e:
            log(f"❌ Error al analizar el XML: {e}")
            return

        log("Análisis completado correctamente.")
        log(f"Título: {result['title']}")
        log(f"Tempo detectado: {result['tempo']} BPM")

        # Delegamos completamente en la vista
        set_voices(result["parts"])

    # ------------------------------------------------------
    # Generar MIDI
    # ------------------------------------------------------
    def generate_midi():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        path = Path(xml_path)

        if not path.is_file():
            log(f"❌ El archivo no existe: {path}")
            return

        selected = get_selected_voices()

        if not selected:
            log("⚠ No hay voces seleccionadas.")
            return

        #output_dir = path.parent / "coral_output"
        """
        output_dir_str = output_dir_var.get().strip()

        if output_dir_str:
            output_dir = Path(output_dir_str)
        else:
            output_dir = path.parent / "coral_output"
        """
        folder_name = folder_name_var.get().strip()
        base_path_str = base_path_var.get().strip()

        if not folder_name:
            log("⚠ El nombre de carpeta no puede estar vacío.")
            return

        # Si no se indica ubicación → usar carpeta del XML
        if base_path_str:
            base_path = Path(base_path_str)
        else:
            base_path = path.parent

        output_dir = base_path / folder_name
        
        log("Generando archivos MIDI...")

        try:
            generated_files = export_selected_parts_to_midi(
                path,
                selected,
                output_dir,
            )

            for file in generated_files:
                log(f"✅ Generado: {file.name}")

            log("Proceso completado correctamente.")

        except Exception as e:
            log(f"❌ Error al generar MIDI: {e}")


    # ------------------------------------------------------
    # Limpiar voces detectadas
    # ------------------------------------------------------
    def clear_detected_voices():
        set_voices([])  # reutilizamos la función existente
        log("Voces limpiadas.")

    # ------------------------------------------------------
    # Generar mezcla MIDI
    # ------------------------------------------------------
    def download_mix_midi():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        path = Path(xml_path)

        if not path.is_file():
            log("❌ El archivo XML no existe.")
            return

        selected = get_selected_voices()

        if not selected:
            log("⚠ No hay voces seleccionadas.")
            return

        mix_levels = get_mix_levels()

        folder_name = folder_name_var.get().strip()
        base_path_str = base_path_var.get().strip()

        if not folder_name:
            log("⚠ El nombre de carpeta no puede estar vacío.")
            return

        if base_path_str:
            base_path = Path(base_path_str)
        else:
            base_path = path.parent

        output_dir = base_path / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        log("Generando mezcla MIDI...")

        try:
            """
            midi_path = export_mix_to_midi(
                path,
                selected,
                mix_levels,
                output_dir,
            )
            """

            default_path = output_dir / "mezcla.mid"

            save_path = filedialog.asksaveasfilename(
                title="Guardar mezcla MIDI",
                defaultextension=".mid",
                initialfile="mezcla.mid",
                initialdir=output_dir,
                filetypes=[("MIDI files", "*.mid")]
            )

            if not save_path:
                log("Operación cancelada.")
                return

            save_path = Path(save_path)

            midi_path = export_mix_to_midi(
                path,
                selected,
                mix_levels,
                save_path,
            )


            log(f"✅ Mezcla MIDI generada: {midi_path.name}")

        except Exception as e:
            log(f"❌ Error al generar mezcla MIDI: {e}")
                        
    # ------------------------------------------------------
    # Examinar ubicación de salida
    # ------------------------------------------------------
    def browse_base_directory():
        from tkinter import filedialog

        folder = filedialog.askdirectory()

        if folder:
            base_path_var.set(folder)
            log(f"Ubicación base seleccionada: {folder}")

    # ------------------------------------------------------
    # Asignar comandos
    # ------------------------------------------------------
    back_btn.config(command=go_back)
    browse_btn.config(command=browse_xml)
    analyze_btn.config(command=analyze)
    view_score_btn.config(command=on_view_score)
    generate_btn.config(command=generate_midi)
    browse_base_btn.config(command=browse_base_directory)
    download_mix_btn.config(command=download_mix_midi)

    root.mainloop()

# ==========================================================
# Controlador de la vista de transcripcion de la GUI
# ==========================================================
def run_transcription_gui():
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
    back_btn = widgets["back_btn"]
    auto_open_var = widgets["auto_open_var"]
    view_in_app_var = widgets["view_in_app_var"]
    view_in_system_var = widgets["view_in_system_var"]


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

            # Preferencias del usuario
            if view_in_app_var.get():
                log("🖥 Visualización directa en la aplicación")
                show_xml_score(original_pdf, pdf_path, mode="app")

            elif view_in_system_var.get():
                log("📂 Visualización directa en visor del sistema")
                #show_xml_score(original_pdf, pdf_path, mode="system")
                _open_with_default_app(pdf_path)

            else:
                # Comportamiento por defecto: mostrar ventana de elección
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
    def go_back():
        root.destroy()
        run_gui()
    # ------------------------------------------------------   


    back_btn.config(command=go_back)
    start_btn.config(command=on_start)
    open_btn.config(command=on_open_output)
    view_xml_btn.config(command=on_view_xml)
    edit_btn.config(command=on_edit)

    root.mainloop()
