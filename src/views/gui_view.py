# src/views/gui_view.py  (Tkinter GUI)
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os

def build_window():
    root = tk.Tk()
    root.title("MusictoSound - Conversor de partituras")
    root.state("zoomed")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text="MusictoSound — Conversor de partituras", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

    # INPUT FILE
    row1 = ttk.Frame(frm)
    row1.pack(fill="x", pady=6)
    ttk.Label(row1, text="Archivo(pdf):", width=20, anchor="w").pack(side="left", padx=(0,5))
    infile_var = tk.StringVar()
    ttk.Entry(row1, textvariable=infile_var, width=90).pack(side="left", padx=6)
    #ttk.Entry(row1, textvariable=infile_var).pack(side="left",padx=6,fill="x",expand=True)

    def browse_file():
        p = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if p:
            infile_var.set(p)

            # Autocompletar carpeta de salida
            folder = os.path.dirname(p)

            # Solo rellenar si está vacío (para no machacar al usuario)
            if not outdir_var.get().strip():
                outdir_var.set(folder)

    ttk.Button(row1, text="Examinar", command=browse_file).pack(side="left")
    view_pdf_btn = ttk.Button(row1, text="Ver pdf original")
    view_pdf_btn.pack(side="left", padx=5)

    # OUTPUT DIR
    row2 = ttk.Frame(frm)
    row2.pack(fill="x", pady=6)
    ttk.Label(row2, text="Carpeta de salida:", width=20, anchor="w").pack(side="left", padx=(0,5))
    outdir_var = tk.StringVar()
    ttk.Entry(row2, textvariable=outdir_var, width=90).pack(side="left", padx=6)

    def browse_folder():
        p = filedialog.askdirectory()
        if p:
            outdir_var.set(p)

    ttk.Button(row2, text="Examinar", command=browse_folder).pack(side="left")
    open_btn = ttk.Button(row2, text="Abrir carpeta")
    open_btn.pack(side="left", padx=5)

    # MODE SELECTION
    mode_var = tk.StringVar(value="auto")
    mode_frame = ttk.LabelFrame(frm, text="Modo de conversión", padding=6)
    mode_frame.pack(fill="x", pady=6)
    ttk.Radiobutton(mode_frame, text="Automático", variable=mode_var, value="auto").pack(side="left", padx=6)
    ttk.Radiobutton(mode_frame, text="Asistido (Audiveris)", variable=mode_var, value="manual").pack(side="left", padx=6)

    # PROGRESS BAR
    progress = ttk.Progressbar(root, mode="indeterminate", length=300)
    progress.pack(pady=6)
    progress.pack_forget()

    # BUTTONS
    bfrm = ttk.Frame(frm)
    bfrm.pack(fill="x", pady=10)

    start_btn = ttk.Button(bfrm, text="Iniciar Trascipción")
    start_btn.pack(side="left", padx=5)

    view_xml_btn = ttk.Button(bfrm, text="Visualizar XML generado")
    view_xml_btn.pack(side="left", padx=5)

    back_btn = ttk.Button(bfrm, text="Volver")
    back_btn.pack(side="right", padx=5)

    edit_btn = ttk.Button(bfrm, text="Editar XML")
    edit_btn.pack(side="left", padx=5)

    analyze_btn = ttk.Button(bfrm, text="Ir a análisis coral")
    analyze_btn.pack(side="left", padx=5)

    quit_btn = ttk.Button(bfrm, text="Salir", command=root.destroy)
    quit_btn.pack(side="right", padx=5)

    # AUTO OPEN OPTIONS
    auto_view_var = tk.BooleanVar(value=True)
    auto_edit_var = tk.BooleanVar(value=True)

    view_in_app_var = tk.BooleanVar(value=False)
    view_in_system_var = tk.BooleanVar(value=False)

    auto_edit_chk = ttk.Checkbutton(
        frm,
        text="Abrir automáticamente el xml generado en el editor",
        variable=auto_edit_var
    )
    auto_edit_chk.pack(anchor="w", pady=(0, 6))

    auto_view_chk = ttk.Checkbutton(
        frm,
        text="Abrir automáticamente el xml generado en el visor",
        variable=auto_view_var
    )
    auto_view_chk.pack(anchor="w")

    def on_view_in_app_toggle():
        if view_in_app_var.get():
            view_in_system_var.set(False)

    def on_view_in_system_toggle():
        if view_in_system_var.get():
            view_in_app_var.set(False)

    view_in_app_chk = ttk.Checkbutton(
        frm,
        text="Visualizar siempre en la aplicación",
        variable=view_in_app_var,
        command=on_view_in_app_toggle
    )
    view_in_app_chk.pack(anchor="w")

    view_in_system_chk = ttk.Checkbutton(
        frm,
        text="Abrir siempre en el visor del sistema",
        variable=view_in_system_var,
        command=on_view_in_system_toggle
    )
    view_in_system_chk.pack(anchor="w", pady=(0, 6))


    # LOG AREA
    ttk.Separator(frm).pack(fill="x", pady=6)
    ttk.Label(frm, text="Registro:").pack(anchor="w")
    log_box = scrolledtext.ScrolledText(frm, height=10, state="disabled")
    log_box.pack(fill="both", expand=True, pady=6)

    # LOG FUNCTION
    def log(message: str):
        log_box.configure(state="normal")
        log_box.insert("end", message + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    # Return all widgets that controller will need
    return {
        "root": root,
        "infile_var": infile_var,
        "outdir_var": outdir_var,
        "mode_var": mode_var,
        "start_btn": start_btn,
        "open_btn": open_btn,
        "view_pdf_btn": view_pdf_btn,
        "view_xml_btn": view_xml_btn,
        "back_btn": back_btn,
        "edit_btn": edit_btn,
        "log": log,
        "auto_view_var": auto_view_var,
        "auto_edit_var": auto_edit_var,
        "view_in_app_var": view_in_app_var,
        "view_in_system_var": view_in_system_var,
        "progress": progress,
        "analyze_btn": analyze_btn,
    }
