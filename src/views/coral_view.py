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

    # ==========================================================
    # ZONA REDIMENSIONABLE (contenido superior + consola)
    # ==========================================================
    paned = ttk.PanedWindow(main_frame, orient="vertical")
    paned.pack(fill="both", expand=True, pady=(10, 0))

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

    generate_btn = ttk.Button(buttons_row, text="Generar MIDI")
    generate_btn.pack(side="left", padx=20, ipady=6)

    download_wav_btn = ttk.Button(buttons_row, text="Descargar WAV")
    download_wav_btn.pack(side="left", padx=20, ipady=6)

    back_btn = ttk.Button(buttons_row, text="Volver")
    back_btn.pack(side="left", padx=20, ipady=6)

    # ===============================
    # Variables para checkbuttons de voces
    # ===============================
    voice_vars = {}
    mix_vars = {}

    def set_voices(parts: list[dict]):
        # Limpiar lista anterior
        for widget in voices_list_frame.winfo_children():
            widget.destroy()
        for widget in mix_list_frame.winfo_children():
            widget.destroy()

        voice_vars.clear()
        mix_vars.clear()

        for part in parts:
            part_id = part["id"]
            part_name = part["name"]

            row_frame = ttk.Frame(voices_list_frame)
            row_frame.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=True)

            chk = ttk.Checkbutton(
                row_frame,
                variable=var
            )
            chk.pack(side="left")

            name_var = tk.StringVar(value=part_name)

            entry = ttk.Entry(
                row_frame,
                textvariable=name_var,
                width=40
            )
            entry.pack(side="left", padx=5, fill="x", expand=True)

            voice_vars[part_id] = {
                "var": var,
                "name_var": name_var
            }

            # Crear slider de mezcla
            mix_row = ttk.Frame(mix_list_frame)
            mix_row.pack(fill="x", pady=2)

            ttk.Label(mix_row, text=part_name, width=15).pack(side="left")

            volume_var = tk.DoubleVar(value=1.0)

            slider = ttk.Scale(
                mix_row,
                from_=0.0,
                to=1.0,
                orient="horizontal",
                variable=volume_var
            )
            slider.pack(side="left", fill="x", expand=True, padx=10)

            mix_vars[part_id] = volume_var

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
            part_id: var.get()
            for part_id, var in mix_vars.items()
        }

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
        "generate_btn": generate_btn,
        "download_wav_btn": download_wav_btn,
        "folder_name_var": folder_name_var,
        "base_path_var": base_path_var,
        "browse_base_btn": browse_base_btn,
    }