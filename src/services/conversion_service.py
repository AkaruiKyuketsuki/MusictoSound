# src/conversion_service.py
from pathlib import Path

from config.config import DEFAULT_OUTPUT_DIR
from models.models import ConversionMode, ConversionRequest, ConversionResult
from providers.audiveris_client import run_audiveris, AudiverisError


def convert_score(request: ConversionRequest) -> ConversionResult:
    """
    Ejecuta el flujo de conversión: entrada PDF -> Audiveris -> MusicXML.
    """
    try:
        output_dir = request.output_dir or DEFAULT_OUTPUT_DIR
        output_file = run_audiveris(
            input_pdf=request.input_path,
            output_dir=output_dir,
            mode=request.mode,
        )

        if request.mode == ConversionMode.FULL_AUTOMATIC:
            if output_file is not None:
                return ConversionResult(
                    success=True,
                    message=f"Conversión completada. Archivo generado: {output_file}",
                    output_file=output_file,
                )
            else:
                return ConversionResult(
                    success=False,
                    message="Audiveris terminó sin errores, pero no se encontró ningún XML en la carpeta de salida.",
                    output_file=None,
                )

        else:
            # Modo manual: probablemente se haya abierto la GUI de Audiveris
            # para corrección manual.
            return ConversionResult(
                success=True,
                message=(
                    "Audiveris se ha lanzado en modo asistido. "
                    "Realiza las correcciones y exporta el MusicXML desde la propia aplicación."
                ),
                output_file=output_file,
            )

    except AudiverisError as e:
        return ConversionResult(success=False, message=str(e), output_file=None)
    except Exception as e:
        # Captura de seguridad
        return ConversionResult(
            success=False,
            message=f"Error inesperado durante la conversión: {e}",
            output_file=None,
        )
