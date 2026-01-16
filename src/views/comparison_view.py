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

    #Variables para la interacción con el ratón
    red_offset_x = 0
    red_offset_y = 0
    red_scale = 1.0

    dragging = False
    drag_start_x = 0
    drag_start_y = 0

    #Variables para la interacción con el ratón
    blue_image_id = None
    red_image_id = None
    handle_id = None

    scale_handle_id = None
    scale_plus_btn = None
    scale_minus_btn = None
    scaling = False
    scale_start_y = 0
    scale_buttons_window_id = None


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
    # Botones de escala de la imagen roja
    # =========================

    def scale_up():
        nonlocal red_scale
        red_scale = min(red_scale * 1.03, 1.2)
        update_images()

    def scale_down():
        nonlocal red_scale
        red_scale = max(red_scale / 1.03, 0.8)
        update_images()

    # =========================
    # Botón de superposición
    # =========================

    def toggle_overlay():
        nonlocal overlay_mode, zoom_level, previous_zoom
        nonlocal red_offset_x, red_offset_y, red_scale

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

            canvas_left.bind("<ButtonPress-1>", on_handle_press)
            canvas_left.bind("<B1-Motion>", on_handle_motion)
            canvas_left.bind("<ButtonRelease-1>", on_handle_release)

            canvas_left.bind("<ButtonPress-3>", on_scale_press)
            canvas_left.bind("<B3-Motion>", on_scale_motion)
            canvas_left.bind("<ButtonRelease-3>", on_scale_release)


        else:
            red_offset_x = 0
            red_offset_y = 0
            red_scale = 1.0

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



    # =========================
    # Funciones de tinte y superposición
    # =========================

    def tint_image(img, tint="red", strength=0.7):
        """
        Aplica un tinte rojo o azul a una imagen RGB.
        strength ∈ [0,1]
        """
        img = img.convert("RGB")
        r, g, b = img.split()

        if tint == "red":
            g = g.point(lambda x: int(x * (1 - strength)))
            b = b.point(lambda x: int(x * (1 - strength)))
        elif tint == "blue":
            r = r.point(lambda x: int(x * (1 - strength)))
            g = g.point(lambda x: int(x * (1 - strength)))

        return Image.merge("RGB", (r, g, b))

    def add_alpha(img, alpha=128):
        """
        Añade canal alpha a una imagen PIL.
        alpha ∈ [0,255]
        """
        img = img.convert("RGBA")
        img.putalpha(alpha)
        return img


    def tinted_overlay(img1, img2, alpha=0.5):
        """
        Superpone img1 (rojo) e img2 (azul)
        """
        img2 = img2.resize(img1.size)

        red_img = tint_image(img1, "red", strength=0.7)
        blue_img = tint_image(img2, "blue", strength=0.7)

        return Image.blend(red_img, blue_img, alpha)

    # =====================================
    # Actualizar imágenes al hacer zoom
    # =====================================

    def update_images():
        nonlocal tk_left, tk_right
        nonlocal blue_image_id, red_image_id, handle_id, scale_handle_id, scale_buttons_window_id

        left_resized = resize_image(left_image, zoom_level)
        right_resized = resize_image(right_image, zoom_level)

        if overlay_mode:

            left_label.configure(image="")
            right_label.configure(image="")
            canvas_left.delete("overlay")

            blue_img = add_alpha(
                tint_image(left_resized, "blue", strength=0.7),
                alpha=120
            )

            right_resized = resize_image(
                right_image,
                zoom_level * red_scale
            )

            red_img = add_alpha(
                tint_image(right_resized, "red", strength=0.7),
                alpha=120
            )


            blue_tk = ImageTk.PhotoImage(blue_img)
            red_tk = ImageTk.PhotoImage(red_img)


            blue_image_id = canvas_left.create_image(
                0, 0, image=blue_tk, anchor="nw", tags="overlay"
            )

            red_image_id = canvas_left.create_image(
                red_offset_x, red_offset_y,
                image=red_tk, anchor="nw", tags="overlay"
            )

            # Botones + / - para escalar
            btn_frame = ttk.Frame(canvas_left)

            scale_plus_btn = ttk.Button(
                btn_frame,
                text="+",
                width=2,
                command=scale_up
            )

            scale_minus_btn = ttk.Button(
                btn_frame,
                text="−",
                width=2,
                command=scale_down
            )

            scale_plus_btn.pack(side="top", padx=1, pady=1)
            scale_minus_btn.pack(side="top", padx=1, pady=1)

            w, _ = red_img.size

            scale_buttons_window_id = canvas_left.create_window(
                red_offset_x + w - 10,
                red_offset_y + 10,
                window=btn_frame,
                anchor="ne",
                tags="overlay"
            )



            handle_id = canvas_left.create_oval(
                red_offset_x - 10, red_offset_y - 10,
                red_offset_x + 10, red_offset_y + 10,
                fill="red", outline="black", width=2,
                tags="overlay"
            )

            right_frame.grid_remove()

            win._images = [blue_tk, red_tk]            

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
    # Eventos del ratón para arrastrar
    # =========================

    def on_handle_press(event):
        nonlocal dragging, drag_start_x, drag_start_y
        
        if not overlay_mode:
            return
        
        if handle_id is None:
            return

        dragging = True
        drag_start_x = event.x
        drag_start_y = event.y


    def on_handle_motion(event):
        nonlocal red_offset_x, red_offset_y, drag_start_x, drag_start_y

        if not dragging or not overlay_mode:
            return

        dx = event.x - drag_start_x
        dy = event.y - drag_start_y

        red_offset_x += dx
        red_offset_y += dy

        drag_start_x = event.x
        drag_start_y = event.y

        canvas_left.coords(
            red_image_id,
            red_offset_x,
            red_offset_y
        )

        canvas_left.coords(
            handle_id,
            red_offset_x - 10, red_offset_y - 10,
            red_offset_x + 10, red_offset_y + 10
        )

        # Mover también los botones + / -
        if scale_buttons_window_id is not None:
            w = int(canvas_left.bbox(red_image_id)[2] - canvas_left.bbox(red_image_id)[0])
            canvas_left.coords(
                scale_buttons_window_id,
                red_offset_x + w - 10,
                red_offset_y + 10
            )



    def on_handle_release(event):
        nonlocal dragging
        dragging = False

    # =========================
    # Eventos del ratón para escalar
    # =========================

    def on_scale_press(event):
        nonlocal scaling, scale_start_y
        if not overlay_mode:
            return
        scaling = True
        scale_start_y = event.y

    def on_scale_motion(event):
        nonlocal red_scale, scale_start_y
        dragging = False

        if not scaling:
            return

        dy = event.y - scale_start_y

        # sensibilidad suave
        red_scale *= 1.0 + dy * 0.002
        red_scale = max(0.8, min(red_scale, 1.2))

        scale_start_y = event.y
        update_images()

    def on_scale_release(event):
        nonlocal scaling
        scaling = False

    


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

    