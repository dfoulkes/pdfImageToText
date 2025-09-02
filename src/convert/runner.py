import click
import boto3
import logging
from boto3.docs.action import document_action
from botocore.exceptions import SSLError, EndpointConnectionError
from pdf2image import convert_from_path
import pytesseract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option('--pdf', default=None,
              help='path to the pdf file to convert to text.')
@click.option('--profile', default=None,
              help='aws profile to use.')
def cli(pdf, profile):
    """Convert Pdf to Text"""
    click.echo("                                                   ")
    click.echo("-----------***************************-------------")
    click.echo("-----------*      Convert Pdf to Text *-------------")
    click.echo("-----------***************************-------------")
    click.echo("                                                   ")

    if profile is None:
        use_profile = 'default'
    else:
        use_profile = profile

    if pdf is None:
        click.echo("Please provide a pdf file to convert using --pdf.")
    else:

        convert_pdf_to_text(pdf,use_profile)
        click.echo("Conversion complete.")

def convert_pdf_to_text(pdf, profile):
    images = convert_from_path(pdf)

    # Extract text from each image
    for image in images:
        text = pytesseract.image_to_string(image, config='--psm 6')  # PSM 6 is for single uniform block of text
        print(text)




