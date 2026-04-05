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

            phoneme_str = result.stdout.strip()

            return self._normalize(phoneme_str)

        except Exception as e:
            return [f"[error]"]

    def _normalize(self, phoneme_str: str) -> list[str]:
        return list(phoneme_str.replace(" ", ""))