import tkinter as tk
from tkinter import ttk, filedialog


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
    # Selector de archivo XML
    # ===============================
    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill="x", pady=10)

    ttk.Label(file_frame, text="Archivo XML:", width=15).pack(side="left")

    xml_path_var = tk.StringVar()

    xml_entry = ttk.Entry(file_frame, textvariable=xml_path_var, width=80)
    xml_entry.pack(side="left", padx=10, fill="x", expand=True)

    browse_btn = ttk.Button(file_frame, text="Examinar")
    browse_btn.pack(side="left")
    
    # ======================================
    # Carpeta de salida (opcional)
    # ======================================
    ttk.Label(
        main_frame,
        text="Carpeta de salida (opcional)",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(15, 5))

    output_frame = ttk.Frame(main_frame)
    output_frame.pack(fill="x", pady=5)

    # Nombre de carpeta
    ttk.Label(output_frame, text="Nombre:", width=10).pack(side="left")

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
    # Botones de acción
    # ===============================
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(pady=20)

    analyze_btn = ttk.Button(buttons_frame, text="Analizar voces")
    analyze_btn.pack(side="left", padx=10, ipady=5)

    view_score_btn = ttk.Button(buttons_frame, text="Visualizar partitura")
    view_score_btn.pack(side="left", padx=10, ipady=5)
    
    # ===============================
    # Frame para mostrar voces
    # ===============================
    """
    voices_frame = ttk.LabelFrame(main_frame, text="Voces detectadas", padding=20)
    voices_frame.pack(fill="both", expand=True, pady=20)
    
    voices_list_frame = ttk.Frame(voices_frame)
    voices_list_frame.pack(fill="both", expand=True)
    """
    # ===============================
    # Zona central (Voces + Mezcla)
    # ===============================
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill="both", expand=True, pady=20)

    # -------- IZQUIERDA: Voces detectadas --------
    voices_frame = ttk.LabelFrame(content_frame, text="Voces detectadas", padding=20)
    voices_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    voices_list_frame = ttk.Frame(voices_frame)
    voices_list_frame.pack(fill="both", expand=True)

    # -------- DERECHA: Mezcla --------
    mixer_frame = ttk.LabelFrame(content_frame, text="Mezcla", padding=20)
    mixer_frame.pack(side="left", fill="both", expand=True)

    mixer_list_frame = ttk.Frame(mixer_frame)
    mixer_list_frame.pack(fill="both", expand=True)

    # Diccionario para sliders
    mixer_vars = {}

    # ===============================
    # Frame inferior de acciones
    # ===============================
    buttons_row = ttk.Frame(main_frame)
    buttons_row.pack(pady=15)

    generate_btn = ttk.Button(buttons_row, text="Generar MIDI")
    generate_btn.pack(side="left", padx=20, ipady=6)

    download_wav_btn = ttk.Button(buttons_row, text="Descargar WAV")
    download_wav_btn.pack(side="left", padx=20, ipady=6)

    back_btn = ttk.Button(buttons_row, text="Volver")
    back_btn.pack(side="left", padx=20, ipady=6)

    # ======================================
    # Variables para checkbuttons de voces
    # ======================================

    voice_vars = {}

    def set_voices(parts: list[dict]):
        # Limpiar voces
        for widget in voices_list_frame.winfo_children():
            widget.destroy()

        # Limpiar mixer
        for widget in mixer_list_frame.winfo_children():
            widget.destroy()

        voice_vars.clear()
        mixer_vars.clear()

        for part in parts:
            part_id = part["id"]
            part_name = part["name"]

            # ---- Columna voces ----
            row_frame = ttk.Frame(voices_list_frame)
            row_frame.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=True)

            chk = ttk.Checkbutton(row_frame, variable=var)
            chk.pack(side="left")

            name_var = tk.StringVar(value=part_name)

            entry = ttk.Entry(
                row_frame,
                textvariable=name_var,
                width=35
            )
            entry.pack(side="left", padx=5, fill="x", expand=True)

            voice_vars[part_id] = {
                "var": var,
                "name_var": name_var
            }

            # ---- Columna mixer ----
            mixer_row = ttk.Frame(mixer_list_frame)
            mixer_row.pack(fill="x", pady=5)

            ttk.Label(mixer_row, text=part_name, width=20).pack(side="left")

            volume_var = tk.DoubleVar(value=1.0)

            slider = ttk.Scale(
                mixer_row,
                from_=0.0,
                to=1.5,
                variable=volume_var,
                orient="horizontal"
            )
            slider.pack(side="left", fill="x", expand=True, padx=5)

            mixer_vars[part_id] = volume_var

    # ============================================
    # Función para obtener voces seleccionadas
    # ============================================            
    def get_selected_voices():
        return [
            {
                "id": part_id,
                "name": data["name_var"].get().strip()
            }
            for part_id, data in voice_vars.items()
            if data["var"].get()
        ]

    # ============================================ 
    # Función para obtener los valores de mezcla
    # ============================================
    def get_mixer_values():
        return {
            part_id: volume_var.get()
            for part_id, volume_var in mixer_vars.items()
        }

    # ===============================
    # Área de registro
    # ===============================
    ttk.Separator(main_frame).pack(fill="x", pady=10)

    ttk.Label(main_frame, text="Registro:").pack(anchor="w")

    log_box = tk.Text(main_frame, height=12, state="disabled")
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
        "back_btn": back_btn,
        "generate_btn": generate_btn,
        "folder_name_var": folder_name_var,
        "base_path_var": base_path_var,
        "browse_base_btn": browse_base_btn,
        "mixer_list_frame": mixer_list_frame,
        "get_mixer_values": get_mixer_values,
        "download_wav_btn": download_wav_btn,
    }