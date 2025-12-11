# src/cli_view.py
from pathlib import Path
from typing import Optional

from models.models import ConversionMode, ConversionResult


def show_welcome() -> None:
    print("==============================")
    print("  Conversor de partituras")
    print("  PDF / imagen -> MusicXML")
    print("==============================\n")


def ask_input_file() -> Path:
    while True:
        raw = input("Introduce la ruta del PDF de la partitura: ").strip().strip('"')
        path = Path(raw)
        if path.is_file():
            return path
        print("❌ El fichero no existe. Inténtalo de nuevo.\n")


def ask_output_dir() -> Path:
    raw = input(
        "Introduce la carpeta de salida para el XML (o deja vacío para usar 'output'): "
    ).strip().strip('"')
    if not raw:
        return Path("output")
    return Path(raw)


def ask_conversion_mode() -> ConversionMode:
    print("\nElige modo de conversión:")
    print("  1) Transcripción completa automática")
    print("  2) Transcripción con posibilidad de corrección (modo asistido)\n")

    while True:
        choice = input("Opción [1-2]: ").strip()
        if choice == "1":
            return ConversionMode.FULL_AUTOMATIC
        if choice == "2":
            return ConversionMode.MANUAL_ASSISTED
        print("Opción no válida. Prueba otra vez.\n")


def show_result(result: ConversionResult) -> None:
    print("\n===== RESULTADO =====")
    print(result.message)
    if result.success and result.output_file:
        print(f"Archivo de salida: {result.output_file}")
    print("=====================\n")
