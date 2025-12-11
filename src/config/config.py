# src/config.py
from pathlib import Path

# Ruta al JAR de Audiveris
# 👉 IMPORTANTE: cámbiala a la ruta real en tu máquina
AUDIVERIS_JAR_PATH: Path = Path(r"C:\Program Files\Audiveris\app\audiveris.jar")

# Carpeta por defecto donde guardar los XML generados
DEFAULT_OUTPUT_DIR: Path = Path("output")

# Aañadir más parámetros aquí (idioma, opciones, etc.)
