from __future__ import annotations

from typing import Any, Sequence

from ocrmypdf.exceptions import BadArgsError

# Map OCRmyPDF/Tesseract language codes to RapidOCR LangRec values.
_DIRECT_LANGUAGE_MAP: dict[str, str] = {
    "ara": "ARABIC",
    "chi_sim": "CH",
    "chi_tra": "CHINESE_CHT",
    "eng": "EN",
    "ell": "EL",
    "gre": "EL",
    "jpn": "JAPAN",
    "kor": "KOREAN",
    "tha": "TH",
    "tam": "TA",
    "tel": "TE",
    "bel": "CYRILLIC",
    "bul": "CYRILLIC",
    "mkd": "CYRILLIC",
    "rus": "CYRILLIC",
    "srp": "CYRILLIC",
    "ukr": "CYRILLIC",
}

_LATIN_LANGUAGE_CODES: set[str] = {
    "afr",
    "cat",
    "ces",
    "dan",
    "deu",
    "est",
    "eus",
    "fin",
    "fra",
    "gle",
    "hrv",
    "hun",
    "ind",
    "isl",
    "ita",
    "lav",
    "lit",
    "mlt",
    "msa",
    "nld",
    "nor",
    "pol",
    "por",
    "ron",
    "slk",
    "slv",
    "spa",
    "sqi",
    "swe",
    "tgl",
    "tur",
    "vie",
}

SUPPORTED_LANGUAGE_CODES: frozenset[str] = frozenset(
    set(_DIRECT_LANGUAGE_MAP) | _LATIN_LANGUAGE_CODES
)


def normalize_languages(languages: Sequence[str] | None) -> list[str]:
    if not languages:
        return ["eng"]
    return [
        str(language).strip().lower() for language in languages if str(language).strip()
    ]


def select_single_language(options: Any) -> str:
    languages = normalize_languages(getattr(options, "languages", None))
    if len(languages) != 1:
        raise BadArgsError(
            "RapidOCR supports exactly one language. "
            "Pass a single language to -l/--language."
        )

    language = languages[0]
    if "+" in language:
        raise BadArgsError(
            "RapidOCR does not support language combinations like eng+fra."
        )

    if language not in SUPPORTED_LANGUAGE_CODES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGE_CODES))
        raise BadArgsError(
            f"Language '{language}' is not supported by ocrmypdf-rapidocr. "
            f"Supported values: {supported}"
        )
    return language


def map_language_to_langrec_name(language: str) -> str:
    normalized = language.lower()
    if normalized in _DIRECT_LANGUAGE_MAP:
        return _DIRECT_LANGUAGE_MAP[normalized]
    if normalized in _LATIN_LANGUAGE_CODES:
        return "LATIN"
    raise KeyError(normalized)
