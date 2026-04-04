from pathlib import Path

from services.coral_parser_service import extract_syllables_by_part


# ==========================================================
# Conversión básica sílaba → fonema
# ==========================================================
def syllable_to_phoneme(syl: str, language: str) -> str:

    s = syl.lower()

    # de momento Auto → Español
    if language == "Auto":
        language = "Español"

    if language == "Español":

        replacements = {
            "que": "ke",
            "qui": "ki",
            "ge": "je",
            "gi": "ji",
            "ce": "ze",
            "ci": "zi",
            "ch": "ch",
            "ll": "y",
            "ñ": "ny",
            "j": "j",
            "v": "b",
            "z": "z",
        }

        for k, v in replacements.items():
            s = s.replace(k, v)

        return s

    # fallback (otros idiomas aún no implementados)
    return s


# ==========================================================
# Conversión completa por voces
# ==========================================================
def extract_phonemes_by_part(xml_path: Path, language: str) -> dict:

    syllables_by_part = extract_syllables_by_part(xml_path)

    phonemes_by_part = {}

    for part, syllables in syllables_by_part.items():

        phonemes = []

        for syl in syllables:
            phon = syllable_to_phoneme(syl, language)
            phonemes.append((syl, phon))

        phonemes_by_part[part] = phonemes

    return phonemes_by_part