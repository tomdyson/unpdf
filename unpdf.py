import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from recipes.registry import registry


def analyze_section(text):
    """Analyze a section header for debugging."""
    print(f"\nSection Analysis:")
    print(f"Text: {text.text}")
    print(f"Level: {text.level}")
    print("Available attributes:", [attr for attr in dir(text) 
          if not attr.startswith('_') and not callable(getattr(text, attr))])
    if hasattr(text, 'parent'):
        print(f"Parent: {text.parent}")
    if hasattr(text, 'children'):
        print(f"Children: {text.children}")


def process_pdf(pdf_path: str, output_path: str = None, recipe: str = "default") -> None:
    """Process a PDF file and save simplified JSON output."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    
    doc_converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            ),
        },
    )
    
    # Get the requested recipe
    conversion_recipe = registry.get_recipe(recipe)
    
    result = doc_converter.convert(pdf_path)
    simplified_doc = conversion_recipe.simplify_document(result.document)
    
    # Determine output path
    if output_path is None:
        output_path = Path(pdf_path).with_suffix('.json')
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified_doc, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_file", help="PDF file to convert")
    parser.add_argument("--recipe", default="default", 
                      choices=registry.list_recipes(),
                      help="Conversion recipe to use")
    args = parser.parse_args()
    
    process_pdf(args.pdf_file, recipe=args.recipe)
