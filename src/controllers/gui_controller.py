# src/controllers/gui_controller.py
import threading
import os
import subprocess
import platform
from pathlib import Path
from tkinter import filedialog
import tempfile
import shutil

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

from services.coral_audio_render_service import midi_to_wav
from concurrent.futures import ThreadPoolExecutor, as_completed

from views.reaper_export_view import show_reaper_export_dialog
from services.reaper_export_service import export_to_reaper_project

from views.reaper_guide_overlay import ReaperGuideOverlay

from views.lyrics_editor_view import open_lyrics_editor
from views.phoneme_viewer_view import open_phoneme_viewer

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
# Crear carpeta única coral_output, coral_output_2, etc.
# ==========================================================
def _create_unique_output_dir(base_path: Path, folder_name: str) -> Path:

    candidate = base_path / folder_name

    if not candidate.exists():
        candidate.mkdir(parents=True)
        return candidate

    counter = 2
    while True:
        new_candidate = base_path / f"{folder_name}_{counter}"

        if not new_candidate.exists():
            new_candidate.mkdir(parents=True)
            return new_candidate

        counter += 1
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
    download_mix_wav_btn = widgets["download_mix_wav_btn"]

    progress = widgets["progress"]
    collapse_controls = widgets["collapse_controls"]
    collapse_file_panel = widgets["collapse_file_panel"]
    get_final_tempo = widgets["get_final_tempo"]
    set_original_tempo = widgets["set_original_tempo"]

    get_pitch_levels = widgets["get_pitch_levels"]
    get_global_transpose = widgets["get_global_transpose"]
    set_initial_key = widgets["set_initial_key"]
    reset_adjustments = widgets["reset_adjustments"]
    get_final_key = widgets["get_final_key"]

    export_reaper_btn = widgets["export_reaper_btn"]

    view_phonemes_btn = widgets["view_phonemes_btn"]
    edit_lyrics_btn = widgets["edit_lyrics_btn"]
    get_voice_models = widgets["get_voice_models"]
    get_voice_enabled = widgets["get_voice_enabled"]
    generate_voice_btn = widgets["generate_voice_btn"]
    
    language_var = widgets["language_var"]

    log("Módulo generador coral listo.")
    current_output_dir = None
    user_selected_base_path = False

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
    # Editor de letra
    # ------------------------------------------------------
    def open_lyrics_editor_window():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML primero.")
            return

        path = Path(xml_path)

        if not path.is_file():
            log("❌ El archivo XML no existe.")
            return

        open_lyrics_editor(root, path, xml_path_var, log)


    # ------------------------------------------------------
    # Visor de fonética
    # ------------------------------------------------------
    def open_phoneme_viewer_window():
        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        open_phoneme_viewer(
            root,
            Path(xml_path),
            language_var.get()
        )

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

            nonlocal current_output_dir

            # 🧹 limpiar carpeta vacía anterior
            if current_output_dir and current_output_dir.exists():

                try:
                    if (
                        current_output_dir.name.startswith("coral_output")
                        and not any(current_output_dir.iterdir())
                    ):
                        current_output_dir.rmdir()
                        log(f"🧹 Carpeta vacía eliminada: {current_output_dir.name}")

                except Exception as e:
                    log(f"⚠ No se pudo limpiar carpeta temporal: {e}")

            current_output_dir = None

            # Obtener carpeta del XML
            xml_dir = Path(path).parent
            nonlocal user_selected_base_path

            # Solo cambiar ubicación automáticamente si el usuario no eligió una manualmente
            if not user_selected_base_path:
                base_path_var.set(str(xml_dir))

            # Limpiar voces anteriores y ajustes
            clear_detected_voices()
            reset_adjustments()

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
        log(f"Tonalidad detectada: {result['key']}")

        set_original_tempo(result["tempo"])
        set_initial_key(result["key"])
        set_voices(result["parts"])

        reset_adjustments()

        nonlocal current_output_dir
        folder_name = folder_name_var.get().strip()
        base_path_str = base_path_var.get().strip()

        if base_path_str:
            base_path = Path(base_path_str)
        else:
            base_path = path.parent
            base_path_var.set(str(base_path))  # mostrar la ruta en la interfaz

        current_output_dir = _create_unique_output_dir(base_path, folder_name)
        
        # Actualizar interfaz con el nombre real de la carpeta
        folder_name_var.set(current_output_dir.name)

        log(f"📁 Carpeta de salida creada: {current_output_dir}")
        collapse_file_panel()
        #collapse_controls()


    # ------------------------------------------------------
    # Generar voces cantadas
    # ------------------------------------------------------
    def generate_voices():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        selected = get_selected_voices()

        if not selected:
            log("⚠ No hay voces seleccionadas.")
            return

        voice_models = get_voice_models()
        voice_enabled = get_voice_enabled()

        log("Generando voces cantadas...")

        for part in selected:

            part_id = part["id"]

            if not voice_enabled.get(part_id, True):
                log(f"⏭ Voz desactivada: {part['name']}")
                continue

            model = voice_models.get(part_id, "Auto")

            log(f"🎤 Generando voz para {part['name']} con modelo {model}")

        log("Proceso de generación vocal iniciado.")
        
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

        if current_output_dir is None:
            log("⚠ Primero analiza la partitura.")
            return

        output_dir = current_output_dir

        log("Generando archivos MIDI...")

        try:
            tempo = get_final_tempo()
            transpose = get_global_transpose()
            pitch_levels = get_pitch_levels()
            final_key = get_final_key()

            generated_files = export_selected_parts_to_midi(
                path,
                selected,
                output_dir,
                tempo_bpm=tempo,
                transpose=transpose,
                pitch_levels=pitch_levels,
                final_key=final_key
            )

            for file in generated_files:
                log(f"✅ Generado: {file.name}")
                log(f"Tempo final aplicado: {tempo} BPM")

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

        if current_output_dir is None:
            log("⚠ Primero analiza la partitura.")
            return

        output_dir = current_output_dir

        log("Generando mezcla MIDI...")

        try:

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

            tempo = get_final_tempo()
            transpose = get_global_transpose()
            pitch_levels = get_pitch_levels()

            midi_path = export_mix_to_midi(
                path,
                selected,
                mix_levels,
                save_path,
                tempo_bpm=tempo,
                transpose=transpose,
                pitch_levels=pitch_levels
            )


            log(f"✅ Mezcla MIDI generada: {midi_path.name}")
            log(f"Tempo final aplicado: {tempo} BPM")

        except Exception as e:
            log(f"❌ Error al generar mezcla MIDI: {e}")

    # ------------------------------------------------------
    # Generar WAV
    # ------------------------------------------------------

    def _convert_midi_to_wav(midi_path, wav_path):
        midi_to_wav(midi_path, wav_path)
        return wav_path

    def generate_wav():

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

        if current_output_dir is None:
            log("⚠ Primero analiza la partitura.")
            return

        output_dir = current_output_dir

        log("Generando WAV de las voces seleccionadas...")

        # crear carpeta temporal
        temp_dir = Path(tempfile.mkdtemp(prefix="midi_temp_"))

        try:

            # 1 generar MIDI temporales
            tempo = get_final_tempo()
            transpose = get_global_transpose()
            pitch_levels = get_pitch_levels()
            final_key = get_final_key()

            midi_files = export_selected_parts_to_midi(
                path,
                selected,
                temp_dir,
                tempo_bpm=tempo,
                transpose=transpose,
                pitch_levels=pitch_levels,
                 final_key=final_key
            )

            # configurar barra de progreso
            total = len(midi_files)
            log(f"🎼 {total} voces seleccionadas para generar WAV.")

            progress["value"] = 0
            progress["maximum"] = total
            progress.update()

            progress["value"] = 0
            progress["maximum"] = total

            # 2 convertir cada MIDI a WAV
            log("🎧 Convirtiendo archivos a WAV (procesamiento paralelo)...")

            #progress.pack(fill="x", padx=50, pady=5)
            futures = []

            with ThreadPoolExecutor(max_workers=2) as executor:

                for midi_path in midi_files:

                    wav_path = output_dir / (midi_path.stem + ".wav")

                    log(f"🎧 Programando conversión: {midi_path.name}")

                    future = executor.submit(_convert_midi_to_wav, midi_path, wav_path)
                    futures.append((future, wav_path))

                completed = 0
                for future in as_completed([f[0] for f in futures]):

                    wav_path = next(w for f, w in futures if f == future)

                    try:
                        future.result()
                        log(f"✅ Generado: {wav_path.name}")
                        #progress["value"] = 0
                    except Exception as e:
                        log(f"❌ Error en {wav_path.name}: {e}")

                    completed += 1
                    log(f"🎧 Progreso: {completed}/{total}")
                    progress["value"] = completed
                    root.update()

            #progress.pack_forget()            
            log("Proceso completado correctamente.")
            
        except Exception as e:
            log(f"❌ Error al generar WAV: {e}")

        finally:
            # eliminar carpeta temporal completa
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    # ------------------------------------------------------
    # Generar mezcla WAV
    # ------------------------------------------------------
    def download_mix_wav():

        xml_path = xml_path_var.get().strip()

        if not xml_path:
            log("⚠ Selecciona un archivo XML.")
            return

        path = Path(xml_path)

        selected = get_selected_voices()

        if not selected:
            log("⚠ No hay voces seleccionadas.")
            return

        mix_levels = get_mix_levels()

        folder_name = folder_name_var.get().strip()
        base_path_str = base_path_var.get().strip()

        if base_path_str:
            base_path = Path(base_path_str)
        else:
            base_path = path.parent

        output_dir = base_path / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # 🔹 diálogo para elegir nombre del WAV
        save_path = filedialog.asksaveasfilename(
            title="Guardar mezcla WAV",
            defaultextension=".wav",
            initialfile="mezcla.wav",
            initialdir=output_dir,
            filetypes=[("WAV files", "*.wav")]
        )

        if not save_path:
            log("Operación cancelada.")
            return

        wav_path = Path(save_path)

        # MIDI temporal
        midi_path = output_dir / "mezcla_temp.mid"

        log("Generando mezcla MIDI temporal...")

        tempo = get_final_tempo()
        transpose = get_global_transpose()
        pitch_levels = get_pitch_levels()

        export_mix_to_midi(
            path,
            selected,
            mix_levels,
            midi_path,
            tempo_bpm=tempo,
            transpose=transpose,
            pitch_levels=pitch_levels
        )

        log("Convirtiendo MIDI a WAV con MuseScore...")

        try:
            midi_to_wav(midi_path, wav_path)

            # borrar archivo temporal
            if midi_path.exists():
                midi_path.unlink()
                log("🧹 Archivo MIDI temporal eliminado.")

            log(f"✅ Mezcla WAV generada: {wav_path.name}")

        except Exception as e:
            log(f"❌ Error al generar WAV: {e}")
    
    # ------------------------------------------------------
    # Exportar a Reaper
    # ------------------------------------------------------
    def export_to_reaper():

        options = show_reaper_export_dialog(root)

        if options is None:
            log("Exportación a Reaper cancelada.")
            return

        log("Opciones de exportación seleccionadas:")

        for key, value in options.items():
            log(f"  {key}: {value}")

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

        log("Preparando exportación a Reaper...")

        try:

            # Obtener valores actuales de la interfaz
            tempo = get_final_tempo()
            transpose = get_global_transpose()
            pitch_levels = get_pitch_levels()
            final_key = get_final_key()

            # Aplicar opciones del diálogo
            if not options["apply_tempo"]:
                tempo = None

            if not options["apply_transpose"]:
                transpose = 0

            export_format = options["format"]
            include_lyrics = options["include_lyrics"]
            
            project_path = export_to_reaper_project(
                root=root,
                xml_path=path,
                selected_parts=selected,
                tempo=tempo,
                transpose=transpose,
                pitch_levels=pitch_levels,
                final_key=final_key,
                export_format=export_format,
                include_lyrics=include_lyrics,
            )

            if project_path:
                log(f"🎛 Proyecto Reaper creado: {project_path.name}")
            else:
                log("Exportación cancelada.")

        except Exception as e:
            log(f"❌ Error al exportar a Reaper: {e}")

    # ------------------------------------------------------
    # Examinar ubicación de salida
    # ------------------------------------------------------
    def browse_base_directory():
        from tkinter import filedialog

        folder = filedialog.askdirectory()

        if folder:
            base_path_var.set(folder)

            nonlocal user_selected_base_path
            user_selected_base_path = True

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
    download_mix_wav_btn.config(command=download_mix_wav)
    download_wav_btn.config(command=generate_wav)
    export_reaper_btn.config(command=export_to_reaper)
    edit_lyrics_btn.config(command=open_lyrics_editor_window)
    view_phonemes_btn.config(command=open_phoneme_viewer_window)
    generate_voice_btn.config(command=generate_voices)

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
    download_wav_btn.config(command=generate_wav)

    root.mainloop()
