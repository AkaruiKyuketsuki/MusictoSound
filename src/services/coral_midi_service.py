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

"""
Genera un MIDI con varias partes combinadas aplicando
los niveles de volumen del mezclador.

Returns:
    Ruta del archivo MIDI generado.

def export_mix_to_midi(
    xml_path: Path,
    selected_parts: list[dict],
    volumes: dict[str, int],
    output_dir: Path,
) -> Path:

    score = converter.parse(xml_path)

    output_dir.mkdir(parents=True, exist_ok=True)

    mix_score = score.__class__()

    selected_map = {p["id"]: p["name"] for p in selected_parts}

    for part in score.parts:

        if part.id in selected_map:

            volume = volumes.get(part.id, 100)

            # Aplicar volumen a todas las notas
            for n in part.recurse().notes:
                if n.volume is None:
                    n.volume = n.volume or {}
                n.volume.velocity = int(volume * 1.27)  # convertir 0-100 → 0-127

            mix_score.insert(0, part)

    midi_path = output_dir / "mezcla.mid"

    mix_score.write("midi", midi_path)

    return midi_path
"""
from music21 import converter, stream
from pathlib import Path


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
            mix_score.insert(0, part)

    midi_path = output_dir / "mezcla.mid"

    mix_score.write("midi", midi_path)

    return midi_path