import subprocess
from .base_converter import BasePhonemeConverter


class EspeakConverter(BasePhonemeConverter):

    def __init__(self, language_code: str):
        self.language_code = language_code

        # Ruta a tu espeak
        self.espeak_path = r"C:\Program Files (x86)\eSpeak\command_line\espeak.exe"

    def convert(self, syllable: str) -> list[str]:

        syllable = syllable.replace("_", "").strip()

        if not syllable:
            return []

        try:
            # Ejecutar espeak con salida fonética
            """
            result = subprocess.run(
                [
                    self.espeak_path,
                    "-q",          # sin audio
                    "--ipa",       # salida IPA
                    "-v", self.language_code,
                    syllable
                ],
                capture_output=True,
                text=True
            )
            """
            result = subprocess.run(
                [
                    self.espeak_path,
                    "-q",          # sin audio
                    "--ipa",       # salida IPA
                    "-v", self.language_code,
                    syllable
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            
            phoneme_str = result.stdout.strip()

            return self._normalize(phoneme_str)

        except Exception as e:
            return [f"[error:{e}]"]

    """
    def _normalize(self, phoneme_str: str) -> list[str]:
        return list(phoneme_str.replace(" ", ""))
    """

    def _normalize(self, phoneme_str: str) -> list[str]:
        phoneme_str = phoneme_str.strip()

        # quitar espacios dobles
        phoneme_str = phoneme_str.replace("  ", " ")

        return phoneme_str.split()    