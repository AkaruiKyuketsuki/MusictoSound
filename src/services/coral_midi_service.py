"""
Servicio encargado de generar archivos MIDI
a partir de partes individuales.
"""
from music21 import converter
from pathlib import Path
from music21 import stream
import copy


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

def export_mix_to_midi(
    xml_path: Path,
    selected_parts: list[dict],
    volumes: dict,
    output_dir: Path,
) -> Path:

    score = converter.parse(xml_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    mix_score = stream.Score()

    selected_ids = {p["id"] for p in selected_parts}

    for part in score.parts:

        if part.id in selected_ids:

            # copiar la parte para no modificar el score original
            part_copy = copy.deepcopy(part)

            volume = volumes.get(part.id, 1.0)

            # ajustar velocity de las notas
            for n in part_copy.recurse().notes:

                if hasattr(n, "volume"):

                    velocity = n.volume.velocity

                    if velocity is None:
                        velocity = 64

                    new_velocity = int(velocity * volume)

                    new_velocity = max(1, min(127, new_velocity))

                    n.volume.velocity = new_velocity

            mix_score.insert(0, part_copy)

    midi_path = output_dir / "mezcla.mid"

    mix_score.write("midi", midi_path)

    return midi_path