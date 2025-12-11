# src/models.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class ConversionMode(Enum):
    FULL_AUTOMATIC = "full_automatic"      # Transcripción directa
    MANUAL_ASSISTED = "manual_assisted"    # Permitir correcciones


@dataclass
class ConversionRequest:
    input_path: Path
    output_dir: Path
    mode: ConversionMode


@dataclass
class ConversionResult:
    success: bool
    message: str
    output_file: Optional[Path] = None
