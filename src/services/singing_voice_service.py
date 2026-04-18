"""
Servicio encargado de generar la estructura necesaria
para síntesis de voces cantadas.

Pipeline:

MusicXML
  ↓
sílabas por voz
  ↓
fonemas por voz
  ↓
notas por voz
  ↓
alineación
  ↓
singing score (debug)
"""

from pathlib import Path
from music21 import converter

from services.phoneme_service import extract_phonemes_by_part


# ==========================================================
# Extraer notas por voz
# ==========================================================
def extract_notes_by_part(xml_path: Path) -> dict:

    score = converter.parse(xml_path)

    notes_by_part = {}
    voice_counter = {}

    for part in score.parts:

        part_name = part.partName.strip() if part.partName else part.id

        # numerar voces duplicadas
        if part_name not in voice_counter:
            voice_counter[part_name] = 1
        else:
            voice_counter[part_name] += 1

        voice_name = f"{part_name} {voice_counter[part_name]}"

        notes = []

        for note in part.recurse().notes:

            if note.isRest:
                continue

            try:
                pitch = note.pitch.midi
            except Exception:
                pitch = None

            duration = float(note.quarterLength)
            offset = float(note.offset)

            notes.append({
                "pitch": pitch,
                "duration": duration,
                "offset": offset
            })

        if notes:
            notes_by_part[voice_name] = notes

    return notes_by_part


# ==========================================================
# Alinear notas y fonemas
# ==========================================================
def align_notes_and_phonemes(notes, phonemes):

    aligned = []

    count = min(len(notes), len(phonemes))

    current_time = 0.0

    for i in range(count):

        note = notes[i]
        phoneme_data = phonemes[i]

        duration = note["duration"]

        aligned.append({
            "syllable": phoneme_data["syllable"],
            "phonemes": phoneme_data["phonemes"],
            "pitch": note["pitch"],
            "duration": duration,
            "offset": current_time
        })

        current_time += duration

    return aligned

# ==========================================================
# Guardar singing score
# ==========================================================
def save_singing_score(score, output_path: Path):

    import json

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(score, f, indent=2, ensure_ascii=False)


# ==========================================================
# Generar voces cantadas (pipeline completo)
# ==========================================================
def generate_singing_voices(
    xml_path: Path,
    selected_parts: list,
    voice_models: dict,
    language: str,
    output_dir: Path,
    log=None
):

    if log:
        log("Extrayendo fonemas por voz...")

    phonemes_by_part = extract_phonemes_by_part(xml_path, language)

    if log:
        log("Extrayendo notas por voz...")

    notes_by_part = extract_notes_by_part(xml_path)

    if log:
        log("Alineando notas y fonemas...")

    for part in selected_parts:

        part_name = part["name"]
        part_id = part["id"]

        if part_name not in phonemes_by_part:
            if log:
                log(f"⚠ No hay fonemas para {part_name}")
            continue

        if part_name not in notes_by_part:
            if log:
                log(f"⚠ No hay notas para {part_name}")
            continue

        phonemes = phonemes_by_part[part_name]
        notes = notes_by_part[part_name]

        aligned = align_notes_and_phonemes(notes, phonemes)

        model = voice_models.get(part_id, "Auto")
        part_dir = output_dir / part_name

        score_path = part_dir / "singing_score.json"
        save_singing_score(aligned, score_path)
        
        lab_path = part_dir / "singing.lab"
        generate_lab_from_score(aligned, lab_path)

        f0_path = part_dir / "singing.f0"
        generate_f0_from_score(aligned, f0_path)

        if log:
            log(f"🎤 Voz preparada: {part_name}")
            log(f"   Modelo: {model}")
            log(f"   Sílabas: {len(aligned)}")
            log(f"   Archivo: {score_path.name}")

    if log:
        log("Proceso de preparación vocal completado.")


# ==========================================================
# Convertir score a label HTS (.lab)
# ==========================================================

def generate_lab_from_score(score, output_path):

    lines = []

    time = 0.0

    # silencio inicial
    sil = 0.2
    start = int(time * 10_000_000)
    end = int((time + sil) * 10_000_000)
    lines.append(f"{start} {end} sil")

    time += sil

    vowels = {"a","e","i","o","u","ɔ","ɛ","ɪ","ʊ","æ","ɑ","ɒ","ə","ɨ"}

    for item in score:

        phonemes = item["phonemes"]
        duration = item["duration"]

        if len(phonemes) == 1:

            start = int(time * 10_000_000)
            end = int((time + duration) * 10_000_000)

            lines.append(f"{start} {end} {phonemes[0]}")

            time += duration

        else:

            # consonantes cortas, vocal larga
            consonant_time = duration * 0.2
            vowel_time = duration * 0.8

            per_consonant = consonant_time / (len(phonemes) - 1)

            for p in phonemes:

                if p in vowels:
                    d = vowel_time
                else:
                    d = per_consonant

                start = int(time * 10_000_000)
                end = int((time + d) * 10_000_000)

                lines.append(f"{start} {end} {p}")

                time += d

    # silencio final
    sil = 0.3
    start = int(time * 10_000_000)
    end = int((time + sil) * 10_000_000)

    lines.append(f"{start} {end} sil")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ==========================================================
# Generar curva de pitch (F0)
# ==========================================================
def generate_f0_from_score(score, output_path, frame_rate=100):

    f0 = []

    for item in score:

        pitch = item["pitch"]
        duration = item["duration"]

        # número de frames
        frames = int(duration * frame_rate)

        if pitch is None:
            pitch = 0

        for _ in range(frames):
            f0.append(pitch)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for value in f0:
            f.write(f"{value}\n")