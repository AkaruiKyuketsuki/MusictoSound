# src/views/comparison_view.py
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pathlib import Path


def show_comparison_view(
    left_image: Image.Image,
    right_image: Image.Image,
    title_left: str = "Partitura original",
    title_right: str = "Partitura generada",
    
):

    """
    Muestra dos imágenes lado a lado con scroll vertical sincronizado.
    """
    zoom_level = 0.6  # 60% al abrir
    overlay_mode = False
    previous_zoom = None

    win = tk.Toplevel()
    win.title("Comparación de partituras")
    win.geometry("1000x700")

    

    # =========================
    # Botones de zoom
    # =========================

    toolbar = ttk.Frame(win)
    toolbar.pack(fill="x", pady=4)

    def zoom_in():
        nonlocal zoom_level
        #zoom_level *= 1.2
        zoom_level = min(zoom_level * 1.2, 3.0)

        update_images()

    def zoom_out():
        nonlocal zoom_level
        #zoom_level /= 1.2
        zoom_level = max(zoom_level / 1.2, 0.2)

        update_images()

    ttk.Button(toolbar, text="Zoom +", command=zoom_in).pack(side="left", padx=4)
    ttk.Button(toolbar, text="Zoom −", command=zoom_out).pack(side="left")

    # =========================
    # Botón de superposición
    # =========================

    def toggle_overlay():
        nonlocal overlay_mode, zoom_level, previous_zoom

        overlay_mode = not overlay_mode

        if overlay_mode:
            # Guardamos el zoom actual
            previous_zoom = zoom_level

            # Aumentamos el zoom x3 (con límite razonable)
            zoom_level = min(zoom_level * 2, 5.0) 

            overlay_btn.config(text="Comparar")
            title_left_label.config(text="Comparación por superposición")

            right_frame.grid_remove()

            container.columnconfigure(0, weight=1)
            container.columnconfigure(1, weight=0)

        else:
            # Restauramos el zoom anterior
            if previous_zoom is not None:
                zoom_level = previous_zoom

            overlay_btn.config(text="Superponer")
            title_left_label.config(text=title_left)

            right_frame.grid(row=0, column=1, sticky="nsew")

            container.columnconfigure(0, weight=1)
            container.columnconfigure(1, weight=1)

        update_images()



    #ttk.Button(toolbar, text="Superponer", command=toggle_overlay).pack(side="left", padx=8)
    overlay_btn = ttk.Button(toolbar, text="Superponer")
    overlay_btn.pack(side="left", padx=8)

    overlay_btn.config(command=toggle_overlay)

    # =========================

    container = ttk.Frame(win)
    container.pack(fill="both", expand=True)

    # =========================
    # Frames izquierdo y derecho
    # =========================
    left_frame = ttk.Frame(container)
    #left_frame.pack(side="left", fill="both", expand=True)

    right_frame = ttk.Frame(container)
    #right_frame.pack(side="left", fill="both", expand=True)

    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(0, weight=1)

    left_frame.grid(row=0, column=0, sticky="nsew")
    right_frame.grid(row=0, column=1, sticky="nsew")


    # =========================
    # Títulos
    # =========================
    #ttk.Label(left_frame, text=title_left, font=("Segoe UI", 10, "bold")).pack(pady=4)
    title_left_label = ttk.Label(
        left_frame,
        text=title_left,
        font=("Segoe UI", 10, "bold")
    )
    title_left_label.pack(pady=4)

    ttk.Label(right_frame, text=title_right, font=("Segoe UI", 10, "bold")).pack(pady=4)

    # =========================
    # Canvas + Scrollbars
    # =========================
    canvas_left = tk.Canvas(left_frame, bg="white")
    canvas_right = tk.Canvas(right_frame, bg="white")

    scrollbar_left = ttk.Scrollbar(left_frame, orient="vertical")
    scrollbar_right = ttk.Scrollbar(right_frame, orient="vertical")

    canvas_left.pack(side="left", fill="both", expand=True)
    scrollbar_left.pack(side="right", fill="y")

    canvas_right.pack(side="left", fill="both", expand=True)
    scrollbar_right.pack(side="right", fill="y")

    # =========================
    # Frames internos
    # =========================
    inner_left = ttk.Frame(canvas_left)
    inner_right = ttk.Frame(canvas_right)

    canvas_left.create_window((0, 0), window=inner_left, anchor="nw")
    canvas_right.create_window((0, 0), window=inner_right, anchor="nw")

    # =========================
    # Imágenes
    # =========================
    #tk_left = ImageTk.PhotoImage(left_image)
    #tk_right = ImageTk.PhotoImage(right_image)
    #ttk.Label(inner_left, image=tk_left).pack(pady=10)
    #ttk.Label(inner_right, image=tk_right).pack(pady=10)

    # =========================
    # Imágenes con zoom
    # =========================
    def resize_image(img, zoom):
        w, h = img.size
        return img.resize((int(w * zoom), int(h * zoom)))

    def blend_images(img1, img2, alpha=0.5):
        # Asegurar mismo tamaño
        img2 = img2.resize(img1.size)
        return Image.blend(img1, img2, alpha)

    left_resized = resize_image(left_image, zoom_level)
    right_resized = resize_image(right_image, zoom_level)

    tk_left = ImageTk.PhotoImage(left_resized)
    tk_right = ImageTk.PhotoImage(right_resized)

    left_label = ttk.Label(inner_left, image=tk_left)
    left_label.pack(pady=10)

    right_label = ttk.Label(inner_right, image=tk_right)
    right_label.pack(pady=10)

    # =====================================
    # Actualizar imágenes al hacer zoom
    # =====================================

    def update_images():
        nonlocal tk_left, tk_right

        left_resized = resize_image(left_image, zoom_level)
        right_resized = resize_image(right_image, zoom_level)

        if overlay_mode:
            blended = blend_images(left_resized, right_resized, alpha=0.5)
            tk_blend = ImageTk.PhotoImage(blended)

            left_label.configure(image=tk_blend)
            right_label.configure(image="")  # ocultamos derecha

            win._images = [tk_blend]
        else:
            tk_left = ImageTk.PhotoImage(left_resized)
            tk_right = ImageTk.PhotoImage(right_resized)

            left_label.configure(image=tk_left)
            right_label.configure(image=tk_right)

            win._images = [tk_left, tk_right]

        inner_left.update_idletasks()
        inner_right.update_idletasks()

        canvas_left.configure(scrollregion=canvas_left.bbox("all"))
        canvas_right.configure(scrollregion=canvas_right.bbox("all"))

    # Evitar garbage collection
    win._images = [tk_left, tk_right]

    
    # =========================
    # Scroll sincronizado
    # =========================
    def _sync_left(*args):
        canvas_left.yview(*args)
        if not overlay_mode:
            canvas_right.yview_moveto(canvas_left.yview()[0])


    def _sync_right(*args):
        canvas_right.yview(*args)
        if not overlay_mode:
            canvas_left.yview_moveto(canvas_right.yview()[0])

    scrollbar_left.config(command=_sync_left)
    scrollbar_right.config(command=_sync_right)

    canvas_left.config(yscrollcommand=scrollbar_left.set)
    canvas_right.config(yscrollcommand=scrollbar_right.set)

    # =========================
    # Rueda del ratón (Windows)
    # =========================
    def _on_mousewheel(event):
        delta = int(-1 * (event.delta / 120))
        canvas_left.yview_scroll(delta, "units")
        canvas_right.yview_scroll(delta, "units")

    win.bind_all("<MouseWheel>", _on_mousewheel)

    # =========================
    # Ajustar región de scroll
    # =========================
    inner_left.update_idletasks()
    inner_right.update_idletasks()

    canvas_left.configure(scrollregion=canvas_left.bbox("all"))
    canvas_right.configure(scrollregion=canvas_right.bbox("all"))

   