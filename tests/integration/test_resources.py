from __future__ import annotations

import json
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pytest
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "resources"
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"


@dataclass
class OcrCase:
    name: str
    input_file: Path
    expected_file: Path
    meta: dict


def discover_cases() -> list[OcrCase]:
    cases = []

    for case_dir in sorted(RESOURCES_DIR.iterdir()):
        if not case_dir.is_dir():
            continue

        meta_file = case_dir / "meta.json"
        expected_file = case_dir / "expected.txt"

        input_candidates = (
            list(case_dir.glob("*.png"))
            + list(case_dir.glob("*.jpg"))
            + list(case_dir.glob("*.jpeg"))
            + list(case_dir.glob("*.pdf"))
        )
        if len(input_candidates) != 1:
            raise ValueError(
                f"{case_dir}: expected exactly one input file, got {len(input_candidates)}"
            )

        meta = (
            json.loads(meta_file.read_text(encoding="utf-8"))
            if meta_file.exists()
            else {}
        )

        cases.append(
            OcrCase(
                name=case_dir.name,
                input_file=input_candidates[0],
                expected_file=expected_file,
                meta=meta,
            )
        )
    return cases


CASES = discover_cases()


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([:,.!?])\s*", r"\1 ", text)
    return " ".join(text.split())


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_ocrmypdf_on_resource_cases(case: OcrCase, debug_output_dir: Path):
    tempfile.tempdir = str(debug_output_dir)

    from ocrmypdf import OcrOptions, ocr

    output_pdf = debug_output_dir / "output.pdf"
    output_text = debug_output_dir / "output.txt"

    options = OcrOptions(
        # Input/output
        input_file=case.input_file,
        output_file=output_pdf,
        sidecar=output_text,
        # Core OCR options
        ocr_engine="rapidocr",
        pdf_renderer="auto",
        languages=case.meta.get("language", []),
        mode="force",
        # Job control
        use_threads=True,
        progress_bar=True,
        quiet=False,
        keep_temporary_files=True,
        # Image processing
        image_dpi=200,
    )

    options.extra_attrs["rapidocr_config_path"] = str(DEFAULT_CONFIG)

    ocr(
        options,
        plugins=["ocrmypdf_rapidocr"],
    )

    assert output_pdf.is_file()
    assert output_text.is_file()

    expected_text = case.expected_file.read_text(encoding="utf-8")
    actual_text = output_text.read_text(encoding="utf-8")
    score = fuzz.ratio(_normalize_text(expected_text), _normalize_text(actual_text))
    min_similarity = case.meta.get("min_similarity", 0.9) * 100

    output_metadata = debug_output_dir / "metadata.json"
    output_metadata.write_text(
        json.dumps(
            {
                "similarity": score,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert score >= min_similarity, (
        f"OCR similarity too low: {score:.2f} < {min_similarity:.2f}\n"
        f"Actual OCR text:\n{actual_text}"
    )