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

    # ===============================
    # Botón Analizar
    # ===============================
    analyze_btn = ttk.Button(main_frame, text="Analizar voces")
    analyze_btn.pack(pady=20, ipady=5)

    # ===============================
    # Frame para mostrar voces
    # ===============================
    voices_frame = ttk.LabelFrame(main_frame, text="Voces detectadas", padding=20)
    voices_frame.pack(fill="both", expand=True, pady=20)
    
    voices_list_frame = ttk.Frame(voices_frame)
    voices_list_frame.pack(fill="both", expand=True)

    # ===============================
    # Variables para checkbuttons de voces
    # ===============================

    voice_vars = {}

    def set_voices(voices: list[str]):
        # limpiar
        for widget in voices_list_frame.winfo_children():
            widget.destroy()

        voice_vars.clear()

        for name in voices:
            var = tk.BooleanVar(value=True)

            chk = ttk.Checkbutton(
                voices_list_frame,
                text=name,
                variable=var
            )
            chk.pack(anchor="w", pady=2)

            voice_vars[name] = var

    def get_selected_voices():
        return [name for name, var in voice_vars.items() if var.get()]

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
        "voices_frame": voices_frame,
        "voices_list_frame": voices_list_frame,
        "set_voices": set_voices,
        "get_selected_voices": get_selected_voices,
        "back_btn": back_btn,
    }