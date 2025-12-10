# src/cli_controller.py
from models import ConversionRequest
from conversion_service import convert_score
from cli_view import (
    show_welcome,
    ask_input_file,
    ask_output_dir,
    ask_conversion_mode,
    show_result,
)


def run_cli() -> None:
    """
    Punto de entrada del modo consola (CLI).
    """
    show_welcome()

    input_path = ask_input_file()
    output_dir = ask_output_dir()
    mode = ask_conversion_mode()

    request = ConversionRequest(
        input_path=input_path,
        output_dir=output_dir,
        mode=mode,
    )

    result = convert_score(request)
    show_result(result)
