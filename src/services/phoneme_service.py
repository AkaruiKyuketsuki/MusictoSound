from pathlib import Path
from services.coral_parser_service import extract_syllables_by_part

from services.phoneme_converters.converter_factory import get_converter

# ==========================================================
# Conversión completa por voces
# ==========================================================
def extract_phonemes_by_part(xml_path: Path, language: str) -> dict:

    syllables_by_part = extract_syllables_by_part(xml_path)

    converter = get_converter(language)

    phonemes_by_part = {}

    for part, syllables in syllables_by_part.items():

        result = []

        for syl in syllables:

            tokens = converter.convert(syl)

            result.append({
                "syllable": syl,
                "phonemes": tokens
            })

        phonemes_by_part[part] = result

    return phonemes_by_part