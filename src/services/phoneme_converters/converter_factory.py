from .espeak_converter import EspeakConverter
from .basque_converter import BasqueConverter


def get_converter(language: str):

    if language == "Auto":
        language = "Español"

    mapping = {
        "Español": "es",
        "Inglés": "en",
        "Francés": "fr",
        "Alemán": "de",
        "Italiano": "it",
        "Portugués": "pt",
        "Ruso": "ru",
        "Latín": "la",
    }

    if language == "Euskera":
        return BasqueConverter()

    if language in mapping:
        return EspeakConverter(mapping[language])

    return EspeakConverter("en")  # fallback