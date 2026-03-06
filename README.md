# ocrmypdf-rapidocr

`ocrmypdf-rapidocr` is an OCRmyPDF plugin that uses [RapidOCR](https://github.com/RapidAI/RapidOCR) as an OCR engine.

## Status

Supported:

- OCR engine integration via OCRmyPDF plugin hooks
- `hOCR` output path (`--pdf-renderer auto` or `--pdf-renderer fpdf2`)
- ONNXRuntime backend only
- Single language selection from `-l/--language`

Not supported:

- `--pdf-renderer sandwich`
- multi-language combinations such as `-l eng+fra`

## Installation

```bash
pip install ocrmypdf-rapidocr
```

Or from source:

```bash
pip install .
```

## Usage

Load the plugin explicitly with `--plugin`:

```bash
ocrmypdf --plugin ocrmypdf_rapidocr -l eng input.pdf output.pdf
```

Optional plugin arguments:

- `--rapidocr-config-path PATH`: use a custom RapidOCR YAML config

Example:

```bash
ocrmypdf \
  --plugin ocrmypdf_rapidocr \
  -l deu \
  input.pdf output.pdf
```

## Language behavior

The plugin uses the first OCRmyPDF language code and maps it to RapidOCR language families.

- direct mappings: `eng`, `chi_sim`, `chi_tra`, `jpn`, `kor`, `ara`, `rus`, `ukr`, `tha`, `tam`, `tel`, `ell`/`gre`
- selected Latin-script codes map to RapidOCR `LATIN`

If a language code is unsupported, OCRmyPDF exits with a clear error message.

## Runtime model downloads

RapidOCR downloads model files on first use when model paths are not pinned in config.
For offline or restricted environments, provide a custom config via
`--rapidocr-config-path` that points to local model files.

## References

- OCRmyPDF plugin API docs: <https://github.com/ocrmypdf/OCRmyPDF/blob/main/docs/plugins.md>
- OCRmyPDF EasyOCR reference plugin: <https://github.com/ocrmypdf/OCRmyPDF-EasyOCR>
- OCRmyPDF AppleOCR reference plugin: <https://github.com/mkyt/OCRmyPDF-AppleOCR>
- OCRmyPDF PaddleOCR reference plugin: <https://github.com/clefru/ocrmypdf-paddleocr>
- RapidOCR project: <https://github.com/RapidAI/RapidOCR>
