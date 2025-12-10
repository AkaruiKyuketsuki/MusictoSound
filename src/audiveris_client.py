# src/audiveris_client.py
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from config import AUDIVERIS_JAR_PATH
from models import ConversionMode

class AudiverisError(Exception):
    """Errores específicos al llamar a Audiveris."""

# Ruta al java.exe embebido que encontraste
AUDIVERIS_EMBEDDED_JAVA = Path(r"C:\Program Files\Audiveris\runtime\bin\java.exe")

def find_java_exe() -> str:
    if AUDIVERIS_EMBEDDED_JAVA.is_file():
        return str(AUDIVERIS_EMBEDDED_JAVA)
    found = shutil.which("java")
    if found:
        return found
    return "java"

def _build_base_command_use_cp() -> list[str]:
    """
    Construye comando usando -cp para incluir TODAS las librerías de la carpeta 'app'
    y arrancar la clase principal 'Audiveris'.
    """
    java_cmd = find_java_exe()
    app_dir = AUDIVERIS_JAR_PATH.parent  # carpeta ...\app
    # En Windows el comodín '*' en classpath incluye todos los jars de la carpeta
    cp_string = f"{str(app_dir)}\\*"
    # Usamos la clase principal 'Audiveris' (stack trace mostró Audiveris.main)
    return [java_cmd, "-cp", cp_string, "Audiveris"]

def _build_base_command_use_jar() -> list[str]:
    """
    Comando alternativo usando -jar (respaldo).
    """
    java_cmd = find_java_exe()
    return [java_cmd, "-jar", str(AUDIVERIS_JAR_PATH)]

def run_audiveris(
    input_pdf: Path,
    output_dir: Path,
    mode: ConversionMode,
) -> Optional[Path]:
    if not AUDIVERIS_JAR_PATH.is_file():
        raise AudiverisError(f"No se encontró el JAR de Audiveris en: {AUDIVERIS_JAR_PATH}")

    if not input_pdf.is_file():
        raise AudiverisError(f"El fichero de entrada no existe: {input_pdf}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Primero intentamos ejecutar usando -cp con todos los jars de la carpeta app
    cmd = _build_base_command_use_cp()

    if mode == ConversionMode.FULL_AUTOMATIC:
        cmd += [
            "-batch",
            "-export",
            "-output", str(output_dir),
            str(input_pdf),
        ]
    else:
        # modo asistido: abrimos el pdf en la UI
        cmd += [str(input_pdf)]

    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        # Si falla por classpath, intentamos de forma segura con -jar como respaldo
        # (algunos paquetes distribuyen un jar "autocontenido" en otras versiones)
        # Guardamos el primer error y probamos con -jar
        first_error = exc
        # Intento con -jar como fallback
        fallback_cmd = _build_base_command_use_jar()
        if mode == ConversionMode.FULL_AUTOMATIC:
            fallback_cmd += [
                "-batch",
                "-export",
                "-output", str(output_dir),
                str(input_pdf),
            ]
        else:
            fallback_cmd += [str(input_pdf)]

        try:
            completed = subprocess.run(
                fallback_cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc2:
            # Ambos intentos fallaron: devolvemos el error combinado para depuración
            raise AudiverisError(
                "Error ejecutando Audiveris (intentado con -cp y con -jar):\n\n"
                f"--- Intento -cp ---\nSTDOUT:\n{first_error.stdout}\nSTDERR:\n{first_error.stderr}\n\n"
                f"--- Intento -jar ---\nSTDOUT:\n{exc2.stdout}\nSTDERR:\n{exc2.stderr}\n"
            ) from exc2

    # Si llegó aquí, el proceso terminó correctamente (o al menos sin excepción)
    if mode == ConversionMode.FULL_AUTOMATIC:
        candidates = list(output_dir.glob("*.mxl")) + list(output_dir.glob("*.xml"))
        if candidates:
            return candidates[0]

    return None
