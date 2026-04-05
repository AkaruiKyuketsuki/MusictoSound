from pathlib import Path
from services.coral_parser_service import extract_syllables_by_part


# ==========================================================
# Dispatcher
# ==========================================================
def syllable_to_phonemes(syl: str, language: str) -> list[str]:

    if language == "Auto":
        language = "Español"

    if language == "Español":
        return spanish_phonemes(syl)

    if language == "Inglés":
        return english_phonemes(syl)

    if language == "Latín":
        return latin_phonemes(syl)

    # fallback
    return [syl.lower()]


# ==========================================================
# Español (base)
# ==========================================================
def spanish_phonemes(s: str) -> list[str]:

    s = s.lower()
    s = s.replace("_", "")  # limpiar melismas

    tokens = []

    i = 0
    while i < len(s):

        # reglas de 2 letras primero
        if s[i:i+2] == "ch":
            tokens.append("ch")
            i += 2
            continue

        if s[i:i+2] == "ll":
            tokens.append("y")
            i += 2
            continue

        if s[i:i+2] == "rr":
            tokens.append("rr")
            i += 2
            continue

        if s[i:i+2] == "qu":
            tokens.append("k")
            i += 2
            continue

        if s[i:i+2] == "gu":
            tokens.append("g")
            i += 2
            continue

        # letras individuales
        c = s[i]

        if c == "c":
            tokens.append("k")

        elif c == "z":
            tokens.append("z")

        elif c == "v":
            tokens.append("b")

        elif c == "ñ":
            tokens.append("ny")

        elif c == "j":
            tokens.append("x")

        else:
            tokens.append(c)

        i += 1

    return tokens


# ==========================================================
# Inglés (placeholder)
# ==========================================================
def english_phonemes(s: str) -> list[str]:
    return list(s.lower())


# ==========================================================
# Latín (placeholder)
# ==========================================================
def latin_phonemes(s: str) -> list[str]:
    return list(s.lower())


# ==========================================================
# Conversión completa por voces
# ==========================================================
def extract_phonemes_by_part(xml_path: Path, language: str) -> dict:

    syllables_by_part = extract_syllables_by_part(xml_path)

    phonemes_by_part = {}

    for part, syllables in syllables_by_part.items():

        result = []

        for syl in syllables:

            tokens = syllable_to_phonemes(syl, language)

            result.append({
                "syllable": syl,
                "phonemes": tokens
            })

        phonemes_by_part[part] = result

    return phonemes_by_part