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
"""
def align_notes_and_phonemes(notes, phonemes):

    aligned = []

    count = min(len(notes), len(phonemes))

    for i in range(count):

        note = notes[i]
        phoneme_data = phonemes[i]

        aligned.append({
            "syllable": phoneme_data["syllable"],
            "phonemes": phoneme_data["phonemes"],
            "pitch": note["pitch"],
            "duration": note["duration"],
            "offset": note["offset"]
        })

    return aligned
"""

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

        if log:
            log(f"🎤 Voz preparada: {part_name}")
            log(f"   Modelo: {model}")
            log(f"   Sílabas: {len(aligned)}")
            log(f"   Archivo: {score_path.name}")

    if log:
        log("Proceso de preparación vocal completado.")