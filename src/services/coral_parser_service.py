"""
Servicio encargado de analizar el MusicXML
y extraer información estructural coral.
"""

from music21 import converter
from pathlib import Path


def analyze_coral_parts(xml_path: Path) -> dict:
    """
    Analiza un archivo MusicXML y devuelve información coral básica.

    Returns:
        {
            "title": str,
            "tempo": float,
            "parts": [str, str, ...]
        }
    """

    score = converter.parse(xml_path)

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
    for i, part in enumerate(score.parts, start=1):
        name = part.partName if part.partName else f"Parte {i}"
        parts.append(name)

    return {
        "title": title,
        "tempo": tempo,
        "parts": parts,
    }

