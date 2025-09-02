import click
import boto3
import logging
import fitz  # PyMuPDF
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.console import Group

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress botocore and boto3 INFO logs for clean CLI output
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)

console = Console()


@click.command()
@click.option('--pdf', required=True, help='Path to the PDF file to process.')
@click.option('--output', default=None, help='Output PDF path (default: adds _with_text suffix).')
@click.option('--profile', default=os.environ.get('PDF_AWS_PROFILE', 'default'), help='AWS profile to use (default: from PDF_AWS_PROFILE env or "default").')
@click.option('--region', default=os.environ.get('PDF_AWS_REGION', 'us-east-1'), help='AWS region (default: from PDF_AWS_REGION env or "us-east-1").')
def cli(pdf, output, profile, region):
    if output is None:
        output = pdf.replace('.pdf', '_with_text.pdf')

    try:
        process_pdf_with_textract(pdf, output, profile, region)
        console.print(f"[bold green]Conversion complete. Output saved to:[/] [underline]{output}[/]", style="green")
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}", style="red")
        raise


def process_pdf_with_textract(pdf_path, output_path, profile, region):
    """Process PDF with AWS Textract and add text overlay"""

    # Initialize AWS session
    session = boto3.Session(profile_name=profile)
    textract = session.client('textract', region_name=region)

    # Open PDF
    doc = fitz.open(pdf_path)
    num_pages = len(doc)

    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    header_text = Align.center("[bold magenta]:page_facing_up: PDF Image To Text[/bold magenta]\n[white]Convert scanned PDFs to searchable text using [bold]AWS Textract[/bold]![/white]", vertical="middle")
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        expand=True,
        console=console,
    )
    task = progress.add_task("[cyan]Processing pages...", total=num_pages)
    group = Group(header_text, progress)
    panel = Panel(group, style="bold cyan", title="[bold yellow]Foulkes PDF OCR converter[/bold yellow]", subtitle="[green]Powered by AWS Textract[/green]", expand=True)
    console.clear()  # Clear terminal before starting Live
    with Live(panel, console=console, refresh_per_second=8, transient=True):
        for page_num in range(num_pages):
            page = doc.load_page(page_num)

            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
            img_data = pix.tobytes("png")

            # Call Textract
            try:
                response = textract.detect_document_text(
                    Document={'Bytes': img_data}
                )

                # Add text overlay to page
                add_text_overlay(page, response, pix.width, pix.height)

            except ClientError as e:
                logger.error(f"Textract error on page {page_num + 1}: {e}")
                continue
            except NoCredentialsError:
                raise Exception("AWS credentials not found. Please configure your AWS profile.")
            progress.update(task, advance=1)

    # Save the modified PDF
    doc.save(output_path)
    doc.close()


def add_text_overlay(page, textract_response, img_width, img_height):
    """Add invisible text overlay to PDF page"""

    # Get page dimensions
    page_rect = page.rect
    scale_x = page_rect.width / img_width
    scale_y = page_rect.height / img_height

    for block in textract_response['Blocks']:
        if block['BlockType'] == 'WORD':
            # Get bounding box
            bbox = block['Geometry']['BoundingBox']

            # Convert to page coordinates
            x0 = bbox['Left'] * img_width * scale_x
            y0 = bbox['Top'] * img_height * scale_y
            x1 = (bbox['Left'] + bbox['Width']) * img_width * scale_x
            y1 = (bbox['Top'] + bbox['Height']) * img_height * scale_y

            # Calculate font size based on bounding box height
            font_size = (y1 - y0) * 0.8

            # Add invisible text
            text = block['Text']
            rect = fitz.Rect(x0, y0, x1, y1)

            # Insert text with invisible rendering mode
            page.insert_text(
                point=(x0, y1 - 2),  # Slight offset from bottom
                text=text,
                fontsize=font_size,
                color=(0, 0, 0),
                render_mode=3  # Invisible text
            )


if __name__ == '__main__':
    cli()