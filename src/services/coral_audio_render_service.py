from pathlib import Path
import subprocess
import shutil

"""
def find_musescore():
    return r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
"""

def find_musescore():
    """
    Busca el ejecutable de MuseScore en el sistema.
    """

    # 1️⃣ Buscar en PATH
    for cmd in ["musescore", "mscore", "mscore3", "mscore4"]:
        path = shutil.which(cmd)
        if path:
            return path

    # 2️⃣ Rutas típicas en Windows
    possible_paths = [
        r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
        r"C:\Program Files\MuseScore 4\bin\musescore.exe",
        r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe",
        r"C:\Program Files\MuseScore 3\bin\mscore3.exe",
    ]

    for path in possible_paths:
        if Path(path).exists():
            return path

    return None

def midi_to_wav(midi_path: Path, wav_path: Path):
    """
    Convierte un archivo MIDI a WAV usando MuseScore.
    """

    musescore = find_musescore()

    if not musescore:
        raise RuntimeError(
            "No se encontró MuseScore en el sistema. Instálalo o añádelo al PATH."
        )

    cmd = [
        musescore,
        str(midi_path),
        "-o",
        str(wav_path)
    ]

    subprocess.run(cmd, check=True)