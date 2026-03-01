"""
Servicio encargado de generar archivos MIDI
a partir de partes individuales.
"""
from music21 import converter
from pathlib import Path

"""
Genera un archivo MIDI por cada parte seleccionada.

Returns:
    Lista de rutas de archivos MIDI generados.
"""
def export_selected_parts_to_midi(
    xml_path: Path,
    selected_parts: list[dict],
    output_dir: Path,
) -> list[Path]:

    score = converter.parse(xml_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Convertimos a diccionario para lookup rápido
    selected_map = {p["id"]: p["name"] for p in selected_parts}

    for part in score.parts:

        if part.id in selected_map:

            display_name = selected_map[part.id]

            safe_name = (
                display_name
                .strip()
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )

            midi_path = output_dir / f"{safe_name}.mid"

            part.write("midi", midi_path)

            generated_files.append(midi_path)

    return generated_files