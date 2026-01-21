# src/views/gui_view.py  (Tkinter GUI)
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

def build_window():
    root = tk.Tk()
    root.title("MusictoSound - Conversor de partituras")
    root.geometry("800x480")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text="MusictoSound — Conversor de partituras", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

    # INPUT FILE
    row1 = ttk.Frame(frm)
    row1.pack(fill="x", pady=6)
    ttk.Label(row1, text="Archivo:", width=10).pack(side="left")
    infile_var = tk.StringVar()
    ttk.Entry(row1, textvariable=infile_var, width=60).pack(side="left", padx=6)
    def browse_file():
        p = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if p:
            infile_var.set(p)
    ttk.Button(row1, text="Examinar", command=browse_file).pack(side="left")

    # OUTPUT DIR
    row2 = ttk.Frame(frm)
    row2.pack(fill="x", pady=6)
    ttk.Label(row2, text="Salida:", width=10).pack(side="left")
    outdir_var = tk.StringVar()
    ttk.Entry(row2, textvariable=outdir_var, width=60).pack(side="left", padx=6)
    def browse_folder():
        p = filedialog.askdirectory()
        if p:
            outdir_var.set(p)
    ttk.Button(row2, text="Examinar", command=browse_folder).pack(side="left")

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

    start_btn = ttk.Button(bfrm, text="Iniciar")
    start_btn.pack(side="left", padx=5)

    open_btn = ttk.Button(bfrm, text="Abrir carpeta salida")
    open_btn.pack(side="left", padx=5)

    view_xml_btn = ttk.Button(bfrm, text="Visualizar XML")
    view_xml_btn.pack(side="left", padx=5)

    edit_btn = ttk.Button(bfrm, text="Edición")
    edit_btn.pack(side="left", padx=5)

    quit_btn = ttk.Button(bfrm, text="Salir", command=root.destroy)
    quit_btn.pack(side="right", padx=5)

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
        "view_xml_btn": view_xml_btn,
        "edit_btn": edit_btn,
        "log": log,
        "progress": progress,
    }
