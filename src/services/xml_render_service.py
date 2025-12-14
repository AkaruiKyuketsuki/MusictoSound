import subprocess
from pathlib import Path

from config.config import MUSESCORE_PATH


def render_xml_to_pdf(xml_path: Path, output_dir: Path) -> Path:
    """
    Convierte un archivo MusicXML en un PDF de partitura usando MuseScore.

    :param xml_path: Ruta al archivo .xml/.musicxml
    :param output_dir: Carpeta donde se generará el PDF
    :return: Ruta al PDF generado
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"No existe el archivo XML: {xml_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / f"{xml_path.stem}.pdf"

    cmd = [
        str(MUSESCORE_PATH),
        str(xml_path),
        "-o",
        str(output_pdf),
    ]

    subprocess.run(cmd, check=True)

    return output_pdf
