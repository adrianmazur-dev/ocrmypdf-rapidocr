from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from ocrmypdf.exceptions import BadArgsError, MissingDependencyError


def is_rapidocr_selected(options: Any) -> bool:
    return getattr(options, "ocr_engine", "auto") in ("auto", "rapidocr")


def add_plugin_options(parser) -> None:
    rapidocr_options = parser.add_argument_group("RapidOCR", "RapidOCR engine options")
    rapidocr_options.add_argument(
        "--rapidocr-config-path",
        default=None,
        help=(
            "Path to a RapidOCR YAML config file. "
            "If omitted, RapidOCR defaults are used."
        ),
    )


def check_runtime_dependencies() -> None:
    if importlib.util.find_spec("rapidocr") is None:
        raise MissingDependencyError(
            "RapidOCR is not installed. Install it with: pip install rapidocr"
        )
    if importlib.util.find_spec("onnxruntime") is None:
        raise MissingDependencyError(
            "onnxruntime is not installed. Install it with: pip install onnxruntime"
        )


def get_option_config_path(options: Any) -> str | None:
    value = getattr(options, "rapidocr_config_path", None)
    if value is None:
        return None
    return str(value)


def validate_plugin_options(options: Any) -> None:
    if getattr(options, "pdf_renderer", "auto") == "sandwich":
        raise BadArgsError("ocrmypdf-rapidocr only supports hOCR/fpdf2 flow. ")

    config_path = get_option_config_path(options)
    if config_path is None:
        return

    path = Path(config_path)
    if not path.exists():
        raise BadArgsError(f"--rapidocr-config-path does not exist: {path}")
    if not path.is_file():
        raise BadArgsError(f"--rapidocr-config-path is not a file: {path}")
