

# Pdf Image To Text Converter

A Python project that converts images in PDF files to text using OCR (Optical Character Recognition).


## Build

```bash
poetry build
```


## Local Install

if still in the poetry environment, first run `deactivate`
Now you can install the built package using pip:
```bash
pip install dist/pdf2txt-0.1.0-py3-none-any.whl
```
>[!NOTE]
> you will need to ensure the python local installation path is in your PATH environment variable

>[!WARNING]
> ensure that the following environment variables are set:
> - PDF_AWS_PROFILE - the AWS profile to use
> - PDF_AWS_REGION - the AWS region to use