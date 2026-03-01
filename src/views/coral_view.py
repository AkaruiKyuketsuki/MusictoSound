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
    voices_frame = ttk.LabelFrame(main_frame, text="Voces detectadas", padding=20)
    voices_frame.pack(fill="both", expand=True, pady=20)
    
    voices_list_frame = ttk.Frame(voices_frame)
    voices_list_frame.pack(fill="both", expand=True)

    # ===============================
    # Botón para generar MIDI
    # ===============================
    generate_btn = ttk.Button(main_frame, text="Generar MIDI")
    generate_btn.pack(pady=10, ipady=5)
    
    # ===============================
    # Variables para checkbuttons de voces
    # ===============================

    voice_vars = {}

    def set_voices(parts: list[dict]):
        # Limpiar lista anterior
        for widget in voices_list_frame.winfo_children():
            widget.destroy()

        voice_vars.clear()

        for part in parts:
            part_id = part["id"]
            part_name = part["name"]

            var = tk.BooleanVar(value=True)

            chk = ttk.Checkbutton(
                voices_list_frame,
                text=part_name,
                variable=var
            )
            chk.pack(anchor="w", pady=2)

            #voice_vars[part_id] = var
            voice_vars[part_id] = {
                "var": var,
                "name": part_name
            }
            
    def get_selected_voices():
        return [
            {
                "id": part_id,
                "name": data["name"]
            }
            for part_id, data in voice_vars.items()
            if data["var"].get()
        ]

    # ===============================
    # Área de registro
    # ===============================
    ttk.Separator(main_frame).pack(fill="x", pady=10)

    ttk.Label(main_frame, text="Registro:").pack(anchor="w")

    log_box = tk.Text(main_frame, height=8, state="disabled")
    log_box.pack(fill="both", expand=False, pady=5)

    def log(message: str):
        log_box.configure(state="normal")
        log_box.insert("end", message + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    # ===============================
    # Botón volver
    # ===============================
    back_btn = ttk.Button(main_frame, text="Volver")
    back_btn.pack(pady=10)

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
        #"output_dir_var": output_dir_var,
        #"browse_output_btn": browse_output_btn,
        "folder_name_var": folder_name_var,
        "base_path_var": base_path_var,
        "browse_base_btn": browse_base_btn,
    }