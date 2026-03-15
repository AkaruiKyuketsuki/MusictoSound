# src/services/reaper_export_service.py

from pathlib import Path
import tempfile
import shutil

from services.coral_midi_service import export_selected_parts_to_midi
from services.coral_audio_render_service import midi_to_wav

import subprocess
import platform
from tkinter import filedialog

import wave

def get_wav_duration(wav_path: Path):

    import struct

    with open(wav_path, "rb") as f:
        f.seek(24)
        sample_rate = struct.unpack("<I", f.read(4))[0]

        f.seek(40)
        data_size = struct.unpack("<I", f.read(4))[0]

        f.seek(34)
        bits_per_sample = struct.unpack("<H", f.read(2))[0]

        f.seek(22)
        channels = struct.unpack("<H", f.read(2))[0]

    bytes_per_sample = bits_per_sample / 8
    total_samples = data_size / (bytes_per_sample * channels)

    duration = total_samples / sample_rate

    return duration


def generate_wavs_for_reaper(
    xml_path: Path,
    selected_parts: list,
    tempo: int,
    transpose: int,
    pitch_levels: dict,
    final_key: str,
):
    """
    Genera archivos WAV temporales para exportación a Reaper.

    Devuelve:
        (temp_dir, wav_files)
    """

    print("XML:", xml_path)
    print("Selected parts:", selected_parts)
    print("Tempo:", tempo)
    print("Transpose:", transpose)
    print("Pitch levels:", pitch_levels)
    print("Final key:", final_key)

    # ==========================================================
    # Crear carpeta temporal
    # ==========================================================

    temp_dir = Path(tempfile.mkdtemp(prefix="reaper_export_"))

    midi_dir = temp_dir / "midi"
    wav_dir = temp_dir / "wav"

    midi_dir.mkdir()
    wav_dir.mkdir()

    # ==========================================================
    # Generar MIDI
    # ==========================================================

    midi_files = export_selected_parts_to_midi(
        xml_path,
        selected_parts,
        midi_dir,
        tempo_bpm=tempo,
        transpose=transpose,
        pitch_levels=pitch_levels,
        final_key=final_key,
    )

    print("MIDI files generated:", midi_files)
    # ==========================================================
    # Convertir a WAV
    # ==========================================================

    wav_files = []

    for midi_path in midi_files:

        wav_path = wav_dir / (midi_path.stem + ".wav")

        midi_to_wav(midi_path, wav_path)

        wav_files.append(wav_path)
    
    print("WAV files generated:", wav_files)

    return temp_dir, wav_files


def create_reaper_project(project_path: Path, wav_files: list[Path]):

    lines = []

    lines.append('<REAPER_PROJECT 0.1 "7.x">')

    for wav in wav_files:

        name = wav.stem
        parts = name.split("_")

        if len(parts) >= 2:
            track_name = f"{parts[0]} {parts[1]}"
        else:
            track_name = parts[0]

        wav_path = str(wav).replace("\\", "/")

        lines.append("<TRACK")
        lines.append(f'NAME "{track_name}"')

        lines.append("<ITEM")
        lines.append("POSITION 0")
        duration = get_wav_duration(wav)
        lines.append(f"LENGTH {duration:.6f}")
        lines.append("LOOP 0")


        lines.append("<SOURCE WAVE")
        lines.append(f'FILE "{wav_path}"')
        lines.append(">")

        lines.append(">")  # close ITEM
        lines.append(">")  # close TRACK

    lines.append(">")

    project_text = "\n".join(lines)

    project_path.write_text(project_text, encoding="utf-8")

    return project_path

def export_to_reaper_project(
    root,
    xml_path: Path,
    selected_parts: list,
    tempo: int,
    transpose: int,
    pitch_levels: dict,
    final_key: str,
):
    """
    Exporta las voces seleccionadas a un proyecto de Reaper.
    """

    # ==========================================================
    # Generar WAV temporales
    # ==========================================================

    temp_dir, wav_files = generate_wavs_for_reaper(
        xml_path,
        selected_parts,
        tempo,
        transpose,
        pitch_levels,
        final_key,
    )

    try:

        # ==========================================================
        # Preguntar dónde guardar el proyecto
        # ==========================================================

        save_path = filedialog.asksaveasfilename(
            parent=root,
            title="Guardar proyecto Reaper",
            defaultextension=".rpp",
            initialfile="proyecto_coral.rpp",
            filetypes=[("Reaper Project", "*.rpp")],
        )

        if not save_path:
            return None

        project_path = Path(save_path)

        # ==========================================================
        # Crear archivo .RPP
        # ==========================================================

        create_reaper_project(project_path, wav_files)

        # ==========================================================
        # Abrir Reaper automáticamente
        # ==========================================================

        _open_reaper(project_path)

        return project_path

    finally:

        # ==========================================================
        # Limpiar carpeta temporal
        # ==========================================================

        #shutil.rmtree(temp_dir, ignore_errors=True)
        pass

def _open_reaper(project_path: Path):

    system = platform.system()

    if system == "Windows":

        possible_paths = [
            r"C:\Program Files\REAPER (x64)\reaper.exe",
            r"C:\Program Files\REAPER\reaper.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\REAPER\reaper.exe",
        ]

        for path in possible_paths:
            if Path(path).exists():
                subprocess.Popen([path, str(project_path)])
                return

        raise FileNotFoundError(
            "No se encontró REAPER. Comprueba que esté instalado."
        )

    elif system == "Darwin":
        subprocess.Popen(["open", "-a", "REAPER", str(project_path)])

    else:
        subprocess.Popen(["reaper", str(project_path)])