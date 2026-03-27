import tkinter as tk
from tkinter import ttk

from services.coral_parser_service import extract_syllables_by_part
#from services.coral_parser_service import apply_lyrics_to_xml
from services.coral_parser_service import create_new_xml_with_lyrics

from tkinter import filedialog
#from tkinter import messagebox

def open_lyrics_editor(parent, xml_path):

    editor = tk.Toplevel(parent)
    editor.title("Editor de letra")
    editor.geometry("900x600")

    main = ttk.Frame(editor, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="Editor de letra",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0,10))

    ttk.Label(
        main,
        text=f"Archivo: {xml_path.name}",
        foreground="gray"
    ).pack(anchor="w", pady=(0,20))

    # ===============================
    # Pestañas de voces
    # ===============================

    notebook = ttk.Notebook(main)
    notebook.pack(fill="both", expand=True)

    # ===============================
    # Cargar sílabas
    # ===============================

    syllables_by_part = extract_syllables_by_part(xml_path)
    
    original_syllables = {
        part: list(sylls)
        for part, sylls in syllables_by_part.items()
    }

    entries_by_part = {}

    for part_name, syllables in syllables_by_part.items():
        
        entries_by_part[part_name] = []

        # Crear pestaña
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=part_name)

        canvas = tk.Canvas(tab)
        canvas.configure(highlightthickness=0)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
        )

        canvas.create_window((0,0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===============================
        # Frame de sílabas
        # ===============================

        part_frame = ttk.Frame(scroll_frame, padding=10)
        part_frame.pack(fill="x", pady=10)

        syllables_per_row = 12
        row = None

        for i, syl in enumerate(syllables):

            if i % syllables_per_row == 0:
                row = ttk.Frame(part_frame)
                row.pack(anchor="w", pady=2)

            entry = ttk.Entry(
                row,
                width=max(len(syl) + 1, 3),
                justify="center"
            )

            entry.insert(0, syl)

            entry.pack(side="left", padx=2)

            entries_by_part[part_name].append(entry)


    """
    def save_lyrics():

        updated_lyrics = {}

        for part_name, entries in entries_by_part.items():

            syllables = []

            for entry in entries:
                syllables.append(entry.get().strip())

            updated_lyrics[part_name] = syllables

        print("\n===== UPDATED LYRICS =====")

        for part, syl in updated_lyrics.items():
            print(part, syl[:10])

        print("==========================\n")

        apply_lyrics_to_xml(xml_path, updated_lyrics)

        print("XML actualizado correctamente.")
    """

    def save_lyrics():

        updated_lyrics = {}

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("MusicXML", "*.xml")],
            title="Guardar XML con nueva letra"
        )

        if not file_path:
            print("Guardado cancelado.")
            return

        for part_name, entries in entries_by_part.items():

            syllables = []

            for entry in entries:
                syllables.append(entry.get().strip())

            updated_lyrics[part_name] = syllables

        #apply_lyrics_to_xml(xml_path, updated_lyrics)
        create_new_xml_with_lyrics(xml_path, file_path, updated_lyrics)

        #messagebox.showinfo("Editor de letra", "Letra guardada correctamente")
        print("Letra guardada correctamente.")

        editor.destroy()

    """
    def revert_changes():
   
        if not messagebox.askyesno(
            "Revertir cambios",
            "¿Seguro que quieres descartar los cambios?"
        ):
            return

        editor.destroy()

        open_lyrics_editor(parent, xml_path)
    """
    
    def revert_changes():

        for part_name, entries in entries_by_part.items():

            original = original_syllables[part_name]

            for entry, text in zip(entries, original):
                entry.delete(0, tk.END)
                entry.insert(0, text)

        print("Cambios revertidos.")
            
    # ===============================
    # Botones inferiores
    # ===============================

    buttons = ttk.Frame(main)
    buttons.pack(fill="x", pady=10)

    ttk.Button(
        buttons,
        text="Revertir cambios",
        command=revert_changes
    ).pack(side="left")


    ttk.Button(
        buttons,
        text="Cerrar",
        command=editor.destroy
    ).pack(side="right")

    ttk.Button(
        buttons,
        text="Guardar",
        command=save_lyrics
    ).pack(side="right", padx=5)    