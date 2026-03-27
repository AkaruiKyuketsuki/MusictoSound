"""
Servicio encargado de analizar el MusicXML
y extraer información estructural coral.
"""

from music21 import converter
from pathlib import Path
from collections import Counter
from music21 import key

#import shutil

# ==========================================================
# Indicaciones musicales que a veces aparecen como lyrics
# ==========================================================

IGNORE_LYRICS = {
    # tempo / tempo changes
    "tempo",
    "a tempo",
    "tempo i",
    "tempo primo",

    # rallentando family
    "rall",
    "rall.",
    "rall. ",
    "rail.",
    "rallentando",
    "poco rall",
    "poco rall.",

    # ritardando family
    "rit",
    "rit.",
    "ritard",
    "ritard.",
    "ritardando",
    "poco rit",
    "poco rit.",

    # accelerando
    "accel",
    "accel.",
    "accelerando",

    # allargando
    "allarg",
    "allarg.",
    "allargando",

    # rubato / expression
    "rubato",

    # poco rail / poco rall style markings
    "poco rail",
    "poco rail.",

    # dynamic style words sometimes exported
    "dolce",
    "espressivo",
    "cantabile",
    "legato",
    "staccato",
    "confuoco",
    "apiacere",
    "a piacere",

    # other musical indications
    "fine",
    "da capo",
    "d.c.",
    "d.c. al fine",
    "dal segno",
    "d.s.",
    "d.s. al fine",

    # repeats
    "bis",

    # expressive
    "sostenuto",
    "marcato",
    "tenuto",
}


def analyze_coral_parts(xml_path: Path) -> dict:
    """
    Analiza un archivo MusicXML y devuelve información coral básica.
    """

    score = converter.parse(xml_path)

    # Detectar tonalidad
    try:
        detected_key = score.analyze("key")
        key_name = f"{detected_key.tonic.name} {detected_key.mode}"
    except Exception:
        key_name = "Desconocida"

    # Título (si existe)
    title = score.metadata.title if score.metadata and score.metadata.title else "Sin título"

    # Tempo inicial
    tempo = 120.0
    try:
        tempo = score.metronomeMarkBoundaries()[0][2].number
    except Exception:
        pass

    # Partes detectadas
    parts = []
    raw_names = []

    for i, part in enumerate(score.parts, start=1):
        raw_name = part.partName.strip() if part.partName else f"Parte {i}"
        raw_names.append(raw_name)

    # Contar ocurrencias
    name_counts = Counter(raw_names)

    # Generar nombres definitivos
    name_counter = {}

    for i, part in enumerate(score.parts, start=1):

        part_id = part.id
        raw_name = raw_names[i - 1]

        if name_counts[raw_name] > 1:
            # Hay duplicados → numerar todos
            if raw_name in name_counter:
                name_counter[raw_name] += 1
            else:
                name_counter[raw_name] = 1

            display_name = f"{raw_name} {name_counter[raw_name]}"
        else:
            display_name = raw_name

        parts.append({
            "id": part_id,
            "name": display_name
        })

    return {
        "title": title,
        "tempo": tempo,
        "parts": parts,
        "key": key_name
    }

def extract_syllables_by_part(xml_path: Path) -> dict:

    score = converter.parse(xml_path)

    syllables_by_part = {}

    voice_counter = {}

    for part in score.parts:

        part_name = part.partName.strip() if part.partName else part.id

        syllables = []

        for note in part.recurse().notes:

            if note.lyrics:

                for lyric in note.lyrics:

                    if lyric.text:
                        #syllables.append(lyric.text.strip())
                        text = lyric.text.strip()

                        # filtrar indicaciones musicales
                        if text.lower() in IGNORE_LYRICS:
                            continue

                        syllables.append(text)

        if syllables:

            # contar voces con mismo nombre
            if part_name not in voice_counter:
                voice_counter[part_name] = 1
            else:
                voice_counter[part_name] += 1

            voice_name = f"{part_name} {voice_counter[part_name]}"

            syllables_by_part[voice_name] = syllables

    return syllables_by_part



def apply_lyrics_to_xml(xml_path, updated_lyrics):
    """
    Aplica las sílabas editadas al MusicXML.
    """
    backup = xml_path.with_suffix(".backup.xml")
    shutil.copy(xml_path, backup)

    score = converter.parse(xml_path)

    part_index = 0

    for part in score.parts:

        part_name = part.partName or f"Voz {part_index+1}"

        if part_name not in updated_lyrics:
            part_index += 1
            continue

        syllables = updated_lyrics[part_name]
        syl_index = 0

        for note in part.recurse().notes:

            if syl_index >= len(syllables):
                break

            text = syllables[syl_index]

            if note.lyrics:

                note.lyrics[0].text = text

            else:

                note.lyric = text

            syl_index += 1

        part_index += 1

    score.write("musicxml", xml_path)



#def create_new_xml_with_lyrics(original_xml, new_xml_path, updated_lyrics):
def create_new_xml_with_lyrics(original_xml, new_xml_path, updated_lyrics, log):    
    """
    Crea un nuevo MusicXML copiando toda la información del original
    pero sustituyendo la letra por la editada en el editor.
    """

    log("Creando nuevo XML con la letra modificada...")

    # Cargar partitura original
    score = converter.parse(original_xml)

    # Contador para numerar voces con mismo nombre
    voice_counter = {}

    for part in score.parts:

        raw_name = part.partName.strip() if part.partName else "Voz"

        # Numerar voces duplicadas
        if raw_name not in voice_counter:
            voice_counter[raw_name] = 1
        else:
            voice_counter[raw_name] += 1

        part_name = f"{raw_name} {voice_counter[raw_name]}"

        # Si esta voz no está en el editor, saltar
        if part_name not in updated_lyrics:
            continue

        syllables = updated_lyrics[part_name]
        syl_index = 0

        # Recorrer notas de la voz
        for note in part.recurse().notes:

            if syl_index >= len(syllables):
                break

            text = syllables[syl_index]

            # Si ya existe lyric → reemplazar
            if note.lyrics:
                note.lyrics[0].text = text
            else:
                note.lyric = text

            syl_index += 1

        #log(f"{part_name}: {syl_index} sílabas aplicadas.")

    # Guardar nuevo XML
    score.write("musicxml", new_xml_path)

    log(f"Nuevo XML guardado en: {new_xml_path}")