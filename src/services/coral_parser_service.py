"""
Servicio encargado de analizar el MusicXML
y extraer información estructural coral.
"""

from music21 import converter
from pathlib import Path
from collections import Counter
from music21 import key


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