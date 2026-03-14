"""
Servicio encargado de generar archivos MIDI
a partir de partes individuales.
"""
from music21 import converter
from pathlib import Path
from music21 import stream
from music21 import tempo
import copy

def apply_tempo(score, bpm: int):
    """
    Aplica un tempo global al score y a cada parte.
    """

    tempo_mark = tempo.MetronomeMark(number=bpm)

    # eliminar tempos existentes
    for el in score.recurse().getElementsByClass(tempo.MetronomeMark):
        if el.activeSite:
            el.activeSite.remove(el)

    # insertar en score
    score.insert(0, tempo_mark)

    # insertar en cada parte
    for part in score.parts:
        part.insert(0, tempo.MetronomeMark(number=bpm))

    return score

""" 
Genera un archivo MIDI por cada parte seleccionada. 
Returns: archivos MIDI generados. 
"""
def export_selected_parts_to_midi(
    xml_path: Path,
    selected_parts: list[dict],
    output_dir: Path,
    tempo_bpm: int | None = None,
    transpose: int = 0,
    pitch_levels: dict | None = None,
    
) -> list[Path]:

    score = converter.parse(xml_path)

    # aplicar transposición global
    if transpose != 0:
        score = score.transpose(transpose)
    
    if tempo_bpm:
        score = apply_tempo(score, tempo_bpm)

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

            if tempo_bpm:
                midi_path = output_dir / f"{safe_name}_{tempo_bpm}bpm.mid"
            else:
                midi_path = output_dir / f"{safe_name}.mid"

            #part.write("midi", midi_path)

            part_copy = copy.deepcopy(part)

            if pitch_levels:
                pitch_shift = pitch_levels.get(part.id, 0)

                if pitch_shift != 0:
                    part_copy = part_copy.transpose(pitch_shift)

            part_copy.write("midi", midi_path)



            generated_files.append(midi_path)

    return generated_files

def export_mix_to_midi(
    xml_path: Path,
    selected_parts: list[dict],
    volumes: dict,
    output_path: Path,
    tempo_bpm: int | None = None,
    transpose: int = 0,
    pitch_levels: dict | None = None,
) -> Path:

    score = converter.parse(xml_path)

    # aplicar transposición global
    if transpose != 0:
        score = score.transpose(transpose)

    if tempo_bpm:
        score = apply_tempo(score, tempo_bpm)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    mix_score = stream.Score()

    selected_ids = {p["id"] for p in selected_parts}

    for part in score.parts:

        if part.id in selected_ids:

            # copiar la parte para no modificar el score original
            part_copy = copy.deepcopy(part)

            if pitch_levels:
                pitch_shift = pitch_levels.get(part.id, 0)

                if pitch_shift != 0:
                    part_copy = part_copy.transpose(pitch_shift)





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

    mix_score.write("midi", output_path)

    return output_path