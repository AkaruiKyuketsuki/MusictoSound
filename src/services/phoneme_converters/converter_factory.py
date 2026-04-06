from .espeak_converter import EspeakConverter
from .basque_converter import BasqueConverter


def get_converter(language: str):

    if language == "None":
        language = "Español"

    mapping = {
        "Español": "es",
        "Latín": "la",
        "Inglés": "en",
        "Alemán": "de",
        "Francés": "fr",
        "Italiano": "it",
        "Portugués": "pt",
        "Catalán": "ca",
        "Euskera": "eu",
        "Holandés": "nl",
        "Polaco": "pl",
        "Checo": "cs",
        "Sueco": "sv",
        "Danés": "da",
        "Noruego": "no",
        "Finlandés": "fi",
        "Ruso": "ru",
        "Ucraniano": "uk",
        "Húngaro": "hu",
        "Rumano": "ro",
        "Turco": "tr",
    }

    if language == "Euskera":
        return BasqueConverter()

    if language in mapping:
        return EspeakConverter(mapping[language])

    return EspeakConverter("en")  # fallback