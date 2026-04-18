"""
Servicio encargado de generar archivos MIDI
a partir de partes individuales.
"""
from music21 import converter
from pathlib import Path
from music21 import stream
from music21 import tempo
import copy

import mido

def insert_lyrics_into_midi(midi_path: Path, part):

    mid = mido.MidiFile(midi_path)
    track = mid.tracks[0]

    ticks_per_beat = mid.ticks_per_beat

    events = []
    abs_time = 0

    # convertir eventos existentes a tiempo absoluto
    for msg in track:
        abs_time += msg.time
        events.append((abs_time, msg))

    # añadir lyrics
    for note in part.recurse().notes:
        if note.lyrics:

            lyric_text = clean_lyric(note.lyrics[0].text)

            #tick = int(note.offset * ticks_per_beat)
            abs_offset = note.getOffsetInHierarchy(part)
            tick = int(abs_offset * ticks_per_beat)

            lyric_msg = mido.MetaMessage(
                "lyrics",
                text=lyric_text,
                time=0
            )

            events.append((tick, lyric_msg))

    # ordenar todos los eventos por tiempo
    events.sort(key=lambda x: x[0])

    # reconstruir track con delta-times correctos
    new_track = mido.MidiTrack()

    last_time = 0

    for abs_time, msg in events:

        delta = abs_time - last_time

        msg.time = delta

        new_track.append(msg)

        last_time = abs_time

    mid.tracks[0] = new_track

    mid.save(midi_path)

def clean_lyric(text: str) -> str:
    """
    Limpia caracteres problemáticos para MIDI (latin-1).
    """

    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "¿": "",
        "¡": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text

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
    final_key: str | None = None,
    
) -> list[Path]:

    score = converter.parse(xml_path)

    # aplicar transposición global
    if transpose != 0:
        score = score.transpose(transpose)

        # normalizar KeySignature para evitar >7 sostenidos o bemoles
        for ks in score.recurse().getElementsByClass("KeySignature"):
            while ks.sharps > 7:
                ks.sharps -= 12
            while ks.sharps < -7:
                ks.sharps += 12
    
    if tempo_bpm:
        score = apply_tempo(score, tempo_bpm)

    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Convertimos a diccionario para lookup rápido
    #selected_map = {p["id"]: p["name"] for p in selected_parts}
    selected_map = {}

    for p in selected_parts:
        real_id = p["id"].split("_")[0]   # 🔥 clave
        selected_map.setdefault(real_id, []).append(p["name"])
        
    part_counter = {}    
    for part in score.parts:

        #if part.id in selected_map:
            #display_name = selected_map[part.id]
        
        if part.id in selected_map:

            names = selected_map[part.id]

            # índice basado en cuántas veces hemos visto esta part
            count = part_counter.get(part.id, 0)

            if count >= len(names):
                continue  # seguridad

            display_name = names[count]

            part_counter[part.id] = count + 1


            safe_name = (
                display_name
                .strip()
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )

            key_suffix = ""
            if final_key:
                key_suffix = "_" + final_key.replace(" ", "")

            if tempo_bpm:
                midi_path = output_dir / f"{safe_name}_{tempo_bpm}bpm{key_suffix}.mid"
            else:
                midi_path = output_dir / f"{safe_name}{key_suffix}.mid"
       
            part_copy = copy.deepcopy(part)

            if pitch_levels:
                pitch_shift = pitch_levels.get(part.id, 0)

                if pitch_shift != 0:
                    part_copy = part_copy.transpose(pitch_shift)

            for note in part_copy.recurse().notes:
                if note.lyrics:
                    lyric_text = note.lyrics[0].text
                    note.lyric = lyric_text
                    #print("SET LYRIC:", lyric_text)
                    #print("NOTE:", note, "LYRIC:", lyric_text)
                    
            # Crear score temporal para asegurar que se exporten las lyrics
            temp_score = stream.Score()
            temp_score.insert(0, part_copy)

            temp_score.write("midi", midi_path)
            insert_lyrics_into_midi(midi_path, part_copy)

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
        
        # normalizar KeySignature para evitar >7 sostenidos o bemoles
        for ks in score.recurse().getElementsByClass("KeySignature"):
            while ks.sharps > 7:
                ks.sharps -= 12
            while ks.sharps < -7:
                ks.sharps += 12

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