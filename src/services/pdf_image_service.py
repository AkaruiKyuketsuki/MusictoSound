# src/services/pdf_image_service.py
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_images(pdf_path: Path, poppler_path: Path | None = None):
    """
    Convierte un PDF en una lista de imágenes PIL.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"No existe el PDF: {pdf_path}")

    images = convert_from_path(
        pdf_path,
        dpi=200,
        poppler_path=str(poppler_path) if poppler_path else None,
    )
    return images
