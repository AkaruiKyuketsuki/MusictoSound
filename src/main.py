# src/main.py
"""
from controllers.cli_controller import run_cli
def main() -> None:
    run_cli()
if __name__ == "__main__":
    main()
"""

# src/main.py
def main() -> None:
    print("Elige modo de ejecución:")
    print("  1) Interfaz gráfica (GUI)")
    print("  2) Línea de comandos (CLI)\n")

    choice = input("Opción [1-2] (enter=GUI): ").strip() or "1"

    if choice == "1":
        try:
            from controllers.gui_controller import run_gui
            run_gui()
            return
        except Exception as e:
            print("Error al lanzar GUI:", e)
            print("Cayendo a CLI...")

    from controllers.cli_controller import run_cli
    run_cli()

if __name__ == "__main__":
    main()
