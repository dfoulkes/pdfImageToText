

# Pdf Image To Text Converter

A Python project that converts images in PDF files to text using OCR (Optical Character Recognition).


## Build

```bash
poetry build
```

## Install

```bash
poetry install
```

## Create Binary
```bash
pip install pyinstaller
pyinstaller --onefile --name pdf2txt src/convert/runner.py
```