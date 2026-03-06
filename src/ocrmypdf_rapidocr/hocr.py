from __future__ import annotations

from html import escape
from typing import Any

HocrLine = tuple[str, tuple[int, int, int, int], int]


def confidence_to_percent(score: Any) -> int:
    if score is None:
        return 0
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0
    if value <= 1.0:
        value *= 100.0
    return max(0, min(100, int(round(value))))


def bbox_from_polygon(polygon: Any, width: int, height: int) -> tuple[int, int, int, int]:
    try:
        points = list(polygon)
    except TypeError:
        return (0, 0, width, height)

    xs: list[float] = []
    ys: list[float] = []
    for point in points:
        try:
            x = float(point[0])
            y = float(point[1])
        except (TypeError, ValueError, IndexError):
            continue
        xs.append(x)
        ys.append(y)

    if not xs or not ys:
        return (0, 0, width, height)

    x0 = max(0, min(width - 1, int(round(min(xs)))))
    y0 = max(0, min(height - 1, int(round(min(ys)))))
    x1 = max(x0 + 1, min(width, int(round(max(xs)))))
    y1 = max(y0 + 1, min(height, int(round(max(ys)))))
    return (x0, y0, x1, y1)


def extract_hocr_lines(
    result: Any,
    *,
    page_width: int,
    page_height: int,
) -> list[HocrLine]:
    boxes_raw = getattr(result, "boxes", None)
    texts_raw = getattr(result, "txts", None)
    scores_raw = getattr(result, "scores", None)

    boxes = list(boxes_raw) if boxes_raw is not None else []
    texts = list(texts_raw) if texts_raw is not None else []
    scores = list(scores_raw) if scores_raw is not None else []
    count = min(len(boxes), len(texts))

    extracted: list[HocrLine] = []
    for index in range(count):
        text = str(texts[index]).strip()
        if not text:
            continue
        box = boxes[index]
        score = scores[index] if index < len(scores) else None
        bbox = bbox_from_polygon(box, page_width, page_height)
        confidence = confidence_to_percent(score)
        extracted.append((text, bbox, confidence))
    return extracted


def build_hocr_document(
    *,
    page_width: int,
    page_height: int,
    language: str,
    lines: list[HocrLine],
) -> str:
    hocr_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"',
        '    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">',
        "<head>",
        "<title></title>",
        '<meta http-equiv="content-type" content="text/html; charset=utf-8" />',
        '<meta name="ocr-system" content="RapidOCR via ocrmypdf-rapidocr" />',
        '<meta name="ocr-capabilities" content="ocr_page ocr_carea ocr_par ocr_line ocrx_word" />',
        "</head>",
        "<body>",
        f'<div class="ocr_page" id="page_1" title="bbox 0 0 {page_width} {page_height}">',
    ]

    for line_id, (text, bbox, confidence) in enumerate(lines, start=1):
        x0, y0, x1, y1 = bbox
        text_escaped = escape(text, quote=False)
        hocr_lines.append(
            f'<div class="ocr_carea" id="carea_{line_id}" title="bbox {x0} {y0} {x1} {y1}">'
        )
        hocr_lines.append(
            f'<p class="ocr_par" id="par_{line_id}" lang="{language}" title="bbox {x0} {y0} {x1} {y1}">'
        )
        hocr_lines.append(
            f'<span class="ocr_line" id="line_{line_id}" '
            f'title="bbox {x0} {y0} {x1} {y1}; baseline 0 0; x_wconf {confidence}">'
        )
        hocr_lines.append(
            f'<span class="ocrx_word" id="word_{line_id}" '
            f'title="bbox {x0} {y0} {x1} {y1}; x_wconf {confidence}">{text_escaped}</span>'
        )
        hocr_lines.extend(["</span>", "</p>", "</div>"])

    hocr_lines.extend(["</div>", "</body>", "</html>"])
    return "\n".join(hocr_lines)
