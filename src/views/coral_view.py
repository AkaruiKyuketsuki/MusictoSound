import tkinter as tk
from tkinter import ttk, filedialog
from music21 import key

from views.lyrics_editor_view import open_lyrics_editor
from views.phoneme_viewer_view import open_phoneme_viewer

def build_coral_view_window():
    root = tk.Tk()
    root.title("MusictoSound - Generador Coral")
    root.state("zoomed")

    main_frame = ttk.Frame(root, padding=40)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        main_frame,
        text="Generador de Pistas de Estudio Coral",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(0, 30))

    # ===============================
    # Panel colapsable de archivo y salida
    # ===============================
    file_container = ttk.Frame(main_frame)
    file_container.pack(fill="x")

    file_header = ttk.Frame(file_container)
    file_header.pack(fill="x")

    file_body = ttk.Frame(file_container)
    file_body.pack(fill="x")

    file_collapsed = tk.BooleanVar(value=False)

    file_toggle_btn = ttk.Button(
        file_header,
        text="▼ Archivo y salida",
        width=25
    )

    file_toggle_btn.pack(anchor="w", pady=(0,5))

    def toggle_file_panel():

        if file_collapsed.get():

            file_body.pack(fill="x")
            file_toggle_btn.config(text="▼ Archivo y salida")
            file_collapsed.set(False)

        else:

            file_body.pack_forget()
            file_toggle_btn.config(text="▶ Archivo y salida")
            file_collapsed.set(True)


    def collapse_file_panel():

        if not file_collapsed.get():

            file_body.pack_forget()

            file_toggle_btn.config(text="▶ Archivo y salida")

            file_collapsed.set(True)

    file_toggle_btn.config(command=toggle_file_panel)

    # ===============================
    # Selector de archivo XML
    # ===============================

    file_frame = ttk.Frame(file_body)
    file_frame.pack(fill="x", pady=10)

    ttk.Label(file_frame, text="Archivo XML:", width=15).pack(side="left")

    xml_path_var = tk.StringVar()

    xml_entry = ttk.Entry(file_frame, textvariable=xml_path_var, width=80)
    xml_entry.pack(side="left", padx=10, fill="x", expand=True)

    browse_btn = ttk.Button(file_frame, text="Examinar")
    browse_btn.pack(side="left")

    # ======================================
    # Carpeta de salida
    # ======================================
    
    output_frame = ttk.Frame(file_body)
    output_frame.pack(fill="x", pady=5)

    # Nombre de carpeta
    ttk.Label(output_frame, text="Nombre (carpeta de salida):", width=25).pack(side="left")

    folder_name_var = tk.StringVar(value="coral_output")

    folder_name_entry = ttk.Entry(
        output_frame,
        textvariable=folder_name_var,
        width=25
    )
    folder_name_entry.pack(side="left", padx=5)

    # Ubicación base
    ttk.Label(output_frame, text="Ubicación:", width=10).pack(side="left", padx=(20, 0))

    base_path_var = tk.StringVar()

    base_path_entry = ttk.Entry(
        output_frame,
        textvariable=base_path_var,
        width=40
    )
    base_path_entry.pack(side="left", padx=5, fill="x", expand=True)

    browse_base_btn = ttk.Button(output_frame, text="Examinar")
    browse_base_btn.pack(side="left", padx=5)

    
    # ===============================
    # Panel colapsable de controles
    # ===============================

    controls_container = ttk.Frame(main_frame)
    controls_container.pack(fill="x")

    controls_header = ttk.Frame(controls_container)
    controls_header.pack(fill="x")

    controls_body = ttk.Frame(controls_container)
    controls_body.pack(fill="x")

    collapsed = tk.BooleanVar(value=False)

    toggle_btn = ttk.Button(
        controls_header,
        text="▼ Controles",
        width=20
    )

    toggle_btn.pack(anchor="w", pady=(0,5))
    
    def toggle_controls():

        if collapsed.get():
            controls_body.pack(fill="x")
            toggle_btn.config(text="▼ Controles")
            collapsed.set(False)

        else:
            controls_body.pack_forget()
            toggle_btn.config(text="▶ Controles")
            collapsed.set(True)

    def collapse_controls():

        if not collapsed.get():
            controls_body.pack_forget()

            toggle_btn.config(
                text="▶ Controles: Tempo, Analizar voces, Visualizar partitura, Volver, Salir"
            )

            collapsed.set(True)
            
    toggle_btn.config(command=toggle_controls)

    # ===============================
    # Botones de acción
    # ===============================

    buttons_frame = ttk.Frame(controls_body)
    buttons_frame.pack(fill="x", pady=20)

    left_frame = ttk.Frame(buttons_frame)
    left_frame.pack(side="left")

    center_frame = ttk.Frame(buttons_frame)
    center_frame.pack(side="left", expand=True)

    right_frame = ttk.Frame(buttons_frame)
    right_frame.pack(side="right")

    # =======================================
    # Frame de tempo y transposición
    # =======================================

    tempo_frame = ttk.LabelFrame(left_frame, text="Tempo", padding=(10,5))
    tempo_frame.pack(side="left")

    transpose_frame = ttk.LabelFrame(left_frame, text="Transposición", padding=(10,5))
    transpose_frame.pack(side="left", padx=(15,0))

    # =======================================

    analyze_btn = ttk.Button(left_frame, text="Analizar voces")
    analyze_btn.pack(side="left", padx=(15,0), ipady=5)

    view_score_btn = ttk.Button(left_frame, text="Visualizar partitura")
    view_score_btn.pack(side="left", padx=(15,0), ipady=5)

    # =======================================
    # Controles de texto y fonética
    # =======================================

    text_tools_frame = ttk.Frame(left_frame)
    text_tools_frame.pack(side="left", padx=(20,0))

    ttk.Label(text_tools_frame, text="Idioma:").pack(side="left")

    language_var = tk.StringVar(value="Auto")

    language_selector = ttk.Combobox(
        text_tools_frame,
        textvariable=language_var,
        values=[
            "Auto",
            "Español",
            "Euskera",
            "Latín",
            "Inglés",
            "Alemán",
            "Italiano",
            "Ruso"
        ],
        width=12,
        state="readonly"
    )

    language_selector.pack(side="left", padx=5)

    view_phonemes_btn = ttk.Button(
        text_tools_frame,
        text="Ver fonética"
    )
    view_phonemes_btn.pack(side="left", padx=5, ipady=5)

    edit_lyrics_btn = ttk.Button(
        text_tools_frame,
        text="Editar letra"
    )
    edit_lyrics_btn.pack(side="left", padx=5, ipady=5)

    back_btn = ttk.Button(buttons_frame, text="Volver")
    back_btn.pack(side="left", padx=10, ipady=5)

    exit_btn = ttk.Button(buttons_frame, text="Salir", command=root.destroy)
    exit_btn.pack(side="left", padx=10, ipady=5)
    
    # ==========================================================
    # ZONA REDIMENSIONABLE (contenido superior + consola)
    # ==========================================================
    paned = ttk.PanedWindow(main_frame, orient="vertical")
    paned.pack(fill="both", expand=True, pady=(10, 0))

    # ===============================
    # Tempo variables
    # ===============================

    original_tempo_var = tk.IntVar(value=120)
    final_tempo_var = tk.IntVar(value=120)
    tempo_adjust_var = tk.IntVar(value=0)

    # Fila 1: Original + Final
    tempo_row1 = ttk.Frame(tempo_frame)
    tempo_row1.pack(anchor="w", pady=2)

    ttk.Label(tempo_row1, text="Original:").pack(side="left")
    ttk.Label(tempo_row1, textvariable=original_tempo_var).pack(side="left")
    ttk.Label(tempo_row1, text=" BPM").pack(side="left", padx=(0,15))

    ttk.Label(tempo_row1, text="Final:").pack(side="left")
    ttk.Label(tempo_row1, textvariable=final_tempo_var).pack(side="left")
    ttk.Label(tempo_row1, text=" BPM").pack(side="left")

    # Fila 2: Ajuste
    tempo_row2 = ttk.Frame(tempo_frame)
    tempo_row2.pack(anchor="w", pady=2)

    ttk.Label(tempo_row2, text="Ajuste:").pack(side="left")

    tempo_spin = ttk.Spinbox(
        tempo_row2,
        from_=-60,
        to=60,
        width=5,
        textvariable=tempo_adjust_var
    )

    tempo_spin.pack(side="left")

    ttk.Label(tempo_row2, text=" BPM").pack(side="left")

    def update_final_tempo(*args):

        original = original_tempo_var.get()

        try:
            adjust = int(tempo_adjust_var.get())
        except (tk.TclError, ValueError):
            return

        final = original + adjust

        if final < 20:
            final = 20

        final_tempo_var.set(final)

    tempo_adjust_var.trace_add("write", update_final_tempo)

    # ===============================
    # Transposición global
    # ===============================

    global_transpose_var = tk.IntVar(value=0)
    initial_key_var = tk.StringVar(value="C major")
    final_key_var = tk.StringVar(value="C major")

    def set_initial_key(key_name: str):
        initial_key_var.set(key_name)
        final_key_var.set(key_name)
    
    # Fila 1: Tonalidad inicial/final
    key_row1 = ttk.Frame(transpose_frame)
    key_row1.pack(anchor="w", pady=2)

    ttk.Label(key_row1, text="Inicial:").pack(side="left")
    ttk.Label(key_row1, textvariable=initial_key_var).pack(side="left")

    ttk.Label(key_row1, text="   Final:").pack(side="left", padx=(10,0))
    ttk.Label(key_row1, textvariable=final_key_var).pack(side="left")

    # Fila 2: Ajuste
    key_row2 = ttk.Frame(transpose_frame)
    key_row2.pack(anchor="w", pady=2)

    ttk.Label(key_row2, text="Ajuste:").pack(side="left")

    transpose_spin = ttk.Spinbox(
        key_row2,
        from_=-12,
        to=12,
        width=5,
        textvariable=global_transpose_var
    )

    transpose_spin.pack(side="left")

    ttk.Label(key_row2, text=" semitonos").pack(side="left")

    # Al cambiar la transposición, actualizar la tonalidad final
    
    def update_final_key(*args):
        try:
            transpose = int(global_transpose_var.get())
        except:
            return

        try:
            key_text = initial_key_var.get()  # "A major"

            tonic, mode = key_text.split()

            current_key = key.Key(tonic, mode)
            new_key = current_key.transpose(transpose)

            #final_key_var.set(f"{new_key.tonic.name} {new_key.mode}")
            tonic = new_key.tonic.name.replace("-", "b")
            final_key_var.set(f"{tonic} {new_key.mode}")

        except Exception as e:
            print("Error transposing key:", e)
            
    global_transpose_var.trace_add("write", update_final_key)

    def reset_adjustments():
        global_transpose_var.set(0)
        tempo_adjust_var.set(0)
    # ===============================
    # Frame superior (contenido)
    # ===============================
    top_frame = ttk.Frame(paned)
    paned.add(top_frame, weight=4)

    # ===============================
    # Frame inferior (registro)
    # ===============================
    bottom_frame = ttk.Frame(paned)
    paned.add(bottom_frame, weight=1)

    def set_initial_pane_size():
        root.update_idletasks()
        total_height = paned.winfo_height()
        console_height = 100  # altura inicial de la consola (puedes ajustar)
        paned.sashpos(0, total_height - console_height)

    root.after(100, set_initial_pane_size)

    # ===============================
    # Contenido principal (voces + mezcla)
    # ===============================
    content_frame = ttk.Frame(top_frame)
    content_frame.pack(fill="both", expand=True)

    # -------------------------------
    # Voces detectadas
    # -------------------------------
    voices_frame = ttk.LabelFrame(content_frame, text="Voces detectadas", padding=20)
    voices_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    voices_list_frame = ttk.Frame(voices_frame)
    voices_list_frame.pack(fill="both", expand=True)

    # -------------------------------
    # Mezcla
    # -------------------------------
    mix_frame = ttk.LabelFrame(content_frame, text="Mezcla", padding=20)
    mix_frame.pack(side="left", fill="both", expand=True)

    mix_list_frame = ttk.Frame(mix_frame)
    mix_list_frame.pack(fill="both", expand=True)

    # ===============================
    # Botones principales
    # ===============================
    buttons_row = ttk.Frame(top_frame)
    buttons_row.pack(pady=15)

    generate_voice_btn = ttk.Button(buttons_row, text="Generar voces")
    generate_voice_btn.pack(side="left", padx=20, ipady=6)

    generate_btn = ttk.Button(buttons_row, text="Generar MIDI")
    generate_btn.pack(side="left", padx=20, ipady=6)

    download_wav_btn = ttk.Button(buttons_row, text="Generar WAV")
    download_wav_btn.pack(side="left", padx=20, ipady=6)

    download_mix_btn = ttk.Button(buttons_row, text="Descargar mezcla")
    download_mix_btn.pack(side="left", padx=20, ipady=6)

    download_mix_wav_btn = ttk.Button(buttons_row, text="Descargar mezcla WAV")
    download_mix_wav_btn.pack(side="left", padx=20, ipady=6)

    export_reaper_btn = ttk.Button(buttons_row, text="Exportar a Reaper")
    export_reaper_btn.pack(side="left", padx=20, ipady=6)

    # La barra se controla desde el controller (gui_controller.py)
    # Solo se muestra si se llama a progress.pack(), en este caso he decidido no mostrarla
    progress = ttk.Progressbar(
        top_frame,
        orient="horizontal",
        mode="determinate"
    )
    progress.pack(fill="x", padx=50, pady=5)
    progress.pack_forget()

    # ===============================
    # Variables para checkbuttons de voces
    # ===============================
    voice_vars = {}
    mix_vars = {}
    pitch_vars = {}
    voice_enable_vars = {}

    def set_voices(parts: list[dict]):
        # Limpiar lista anterior
        for widget in voices_list_frame.winfo_children():
            widget.destroy()
        for widget in mix_list_frame.winfo_children():
            widget.destroy()

        voice_vars.clear()
        mix_vars.clear()
        pitch_vars.clear()
        voice_enable_vars.clear()


        for part in parts:
            part_id = part["id"]
            part_name = part["name"]

            row_frame = ttk.Frame(voices_list_frame)
            row_frame.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(row_frame, variable=var)
            chk.pack(side="left")

            name_var = tk.StringVar(value=part_name)

            entry = ttk.Entry(
                row_frame,
                textvariable=name_var,
                width=40
            )
            entry.pack(side="left", padx=5, fill="x", expand=True)

            # ===============================
            model_var = tk.StringVar(value="Auto")

            model_selector = ttk.Combobox(
                row_frame,
                textvariable=model_var,
                values=[
                    "Auto",
                    "Soprano AI",
                    "Alto AI",
                    "Tenor AI",
                    "Bajo AI",
                    "Neutral Voice"
                ],
                width=14,
                state="readonly"
            )

            model_selector.pack(side="left", padx=5)
            # ================================


            voice_vars[part_id] = {
                "var": var,
                "name_var": name_var,
                "model_var": model_var
            }

            # Crear slider de mezcla
            mix_row = ttk.Frame(mix_list_frame)
            mix_row.pack(fill="x", pady=2)

            mix_label = ttk.Label(mix_row, textvariable=name_var, width=25)
            mix_label.pack(side="left")

            # Volumen 0-100 con sincronización slider + spinbox
            volume_var = tk.IntVar(value=100)

            slider = ttk.Scale(
                mix_row,
                from_=0,
                to=100,
                orient="horizontal"
            )
            
            #slider.pack(side="left", fill="x", expand=True, padx=10)
            slider.pack(side="left", fill="x", expand=True, padx=(10,5))

            spin = ttk.Spinbox(
                mix_row,
                from_=0,
                to=100,
                width=5,
                textvariable=volume_var
            )

            spin.pack(side="left", padx=5)
            ttk.Label(mix_row, text="Vol").pack(side="left", padx=(0,10))


            # ===============================
            # Pitch por pista
            # ===============================

            pitch_var = tk.IntVar(value=0)

            pitch_spin = ttk.Spinbox(
                mix_row,
                from_=-12,
                to=12,
                width=5,
                textvariable=pitch_var
            )

            pitch_spin.pack(side="left", padx=(10,5))
            ttk.Label(mix_row, text="Pitch").pack(side="left", padx=(0,10))

            # Checkbutton para habilitar/deshabilitar voz
            voice_enabled_var = tk.BooleanVar(value=True)

            voice_check = ttk.Checkbutton(
                mix_row,
                text="Voz",
                variable=voice_enabled_var
            )

            voice_check.pack(side="left", padx=(10,0))

            voice_enable_vars[part_id] = voice_enabled_var
            pitch_vars[part_id] = pitch_var

            # =============================
            # Sincronización slider + spinbox
            # =============================

            
            # sincronizar slider → variable
            def on_slider(val, var=volume_var):
                var.set(int(float(val)))

            slider.config(command=on_slider)

            # sincronizar variable → slider
            def update_slider(*args, s=slider, var=volume_var):
                s.set(var.get())

            volume_var.trace_add("write", update_slider)

            slider.set(100)

            mix_vars[part_id] = volume_var

            def toggle_voice(v=var, vol=volume_var, s=slider, sp=spin, ps=pitch_spin, lbl=mix_label, name=name_var):
                if v.get():
                    vol.set(100)
                    s.state(["!disabled"])
                    sp.state(["!disabled"])
                    ps.state(["!disabled"])
                    s.set(100)
                    pitch_var.set(0)
                    lbl.configure(text=name.get(), foreground="black")
                else:
                    vol.set(0)
                    s.state(["disabled"])
                    sp.state(["disabled"])
                    ps.state(["disabled"])
                    lbl.configure(text=f"{name.get()} (mute)", foreground="gray")

            chk.config(command=toggle_voice)

    def get_selected_voices():
        return [
            {
                "id": part_id,
                "name": data["name_var"].get().strip()
            }
            for part_id, data in voice_vars.items()
            if data["var"].get()
        ]

    def get_mix_levels():
        return {
            part_id: var.get() / 100
            for part_id, var in mix_vars.items()
        }


    def get_pitch_levels():
        return {
            part_id: var.get()
            for part_id, var in pitch_vars.items()
        }

    def get_voice_models():
        return {
            part_id: data["model_var"].get()
            for part_id, data in voice_vars.items()
        }
            

    def get_voice_enabled():
        return {
            part_id: var.get()
            for part_id, var in voice_enable_vars.items()
        }

    def get_final_tempo():
        return final_tempo_var.get()

    def get_global_transpose():
        return global_transpose_var.get()

    def get_final_key():
        return final_key_var.get()

    def set_original_tempo(bpm: int):
        original_tempo_var.set(int(bpm))
        update_final_tempo()
        
    # ===============================
    # Registro
    # ===============================

    # Pequeño indicador visual de arrastre
    drag_indicator = ttk.Frame(bottom_frame)
    drag_indicator.pack(fill="x", pady=(2, 4))

    indicator_line = tk.Frame(drag_indicator, height=2, bg="#999999")
    indicator_line.pack(fill="x", padx=200, pady=2)

    ttk.Label(bottom_frame, text="Registro:").pack(anchor="w")

    log_box = tk.Text(bottom_frame, height=8, state="disabled")
    log_box.pack(fill="both", expand=True, pady=5)

    def log(message: str):
        log_box.configure(state="normal")
        log_box.insert("end", message + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    return {
        "root": root,
        "xml_path_var": xml_path_var,
        "log": log,
        "browse_btn": browse_btn,
        "analyze_btn": analyze_btn,
        "view_score_btn": view_score_btn,
        "voices_frame": voices_frame,
        "voices_list_frame": voices_list_frame,
        "set_voices": set_voices,
        "get_selected_voices": get_selected_voices,
        "get_mix_levels": get_mix_levels,
        "back_btn": back_btn,
        "exit_btn": exit_btn,
        "generate_btn": generate_btn,
        "download_wav_btn": download_wav_btn,
        "folder_name_var": folder_name_var,
        "base_path_var": base_path_var,
        "browse_base_btn": browse_base_btn,
        "download_mix_btn": download_mix_btn,
        "download_mix_wav_btn": download_mix_wav_btn,
        "progress": progress,
        "get_final_tempo": get_final_tempo,
        "set_original_tempo": set_original_tempo,
        "collapse_controls": collapse_controls,
        "collapse_file_panel": collapse_file_panel,
        "get_pitch_levels": get_pitch_levels,
        "get_global_transpose": get_global_transpose,
        "set_initial_key": set_initial_key,
        "reset_adjustments": reset_adjustments,
        "get_final_key": get_final_key,
        "export_reaper_btn": export_reaper_btn,
        "language_var": language_var,
        "edit_lyrics_btn": edit_lyrics_btn,
        "view_phonemes_btn": view_phonemes_btn,
        "get_voice_models": get_voice_models,
        "get_voice_enabled": get_voice_enabled,
        "generate_voice_btn": generate_voice_btn,
    }