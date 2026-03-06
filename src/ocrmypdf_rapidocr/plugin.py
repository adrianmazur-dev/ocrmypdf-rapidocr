from __future__ import annotations

import logging

from ocrmypdf import hookimpl

from ocrmypdf_rapidocr.engine import RapidOCREngine
from ocrmypdf_rapidocr.languages import select_single_language
from ocrmypdf_rapidocr.options import (
    add_plugin_options,
    check_runtime_dependencies,
    is_rapidocr_selected,
    validate_plugin_options,
)

log = logging.getLogger(__name__)


@hookimpl
def add_options(parser) -> None:
    add_plugin_options(parser)


@hookimpl
def check_options(options) -> None:
    if not is_rapidocr_selected(options):
        return

    check_runtime_dependencies()
    validate_plugin_options(options)
    select_single_language(options)


@hookimpl
def get_ocr_engine(options=None):
    if options is not None:
        ocr_engine = getattr(options, "ocr_engine", "auto")
        if ocr_engine not in ("auto", "rapidocr"):
            return None
    return RapidOCREngine()
