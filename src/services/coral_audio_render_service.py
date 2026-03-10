
"""
Servicio de renderizado de audio coral (WAV)
Actualmente deshabilitado.
"""


"""
from pathlib import Path
import subprocess
import wave
import numpy as np

MUSESCORE_PATH = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

from music21 import converter
import tempfile


def generate_temp_midis_from_xml(xml_path: Path, selected_parts: list[dict]):
    score = converter.parse(xml_path)

    midi_paths = []

    for part_info in selected_parts:
        part_id = part_info["id"]

        part = score.parts[part_id]

        tmp = tempfile.NamedTemporaryFile(suffix=".mid", delete=False)
        tmp_path = Path(tmp.name)
        part.write("midi", tmp_path)

        midi_paths.append(tmp_path)

    return midi_paths

def midi_to_wav(midi_path: Path, wav_path: Path):
    subprocess.run(
        [
            MUSESCORE_PATH,
            str(midi_path),
            "-o",
            str(wav_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def load_wav_as_array(path: Path):
    with wave.open(str(path), "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        audio = wf.readframes(n_frames)

    audio_array = np.frombuffer(audio, dtype=np.int16)

    if n_channels == 2:
        audio_array = audio_array.reshape(-1, 2)

    return audio_array, framerate, n_channels


def save_array_as_wav(path: Path, audio_array, framerate, n_channels):
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(audio_array.astype(np.int16).tobytes())


def mix_wavs(
    midi_files: list[Path],
    volumes: list[float],
    output_path: Path,
):
    wav_arrays = []
    framerate = None
    n_channels = None

    for midi_path in midi_files:
        wav_path = midi_path.with_suffix(".wav")
        midi_to_wav(midi_path, wav_path)

        audio_array, framerate, n_channels = load_wav_as_array(wav_path)
        wav_arrays.append(audio_array)

    # Igualar longitudes
    max_length = max(arr.shape[0] for arr in wav_arrays)

    padded_arrays = []
    for arr, vol in zip(wav_arrays, volumes):
        padded = np.zeros((max_length, n_channels), dtype=np.float32)
        padded[: arr.shape[0]] = arr * vol
        padded_arrays.append(padded)

    mixed = np.sum(padded_arrays, axis=0)

    # Evitar clipping
    mixed = np.clip(mixed, -32768, 32767)

    save_array_as_wav(output_path, mixed, framerate, n_channels)
"""