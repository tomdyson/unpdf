import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


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


def infer_section_level(title: str, prev_title: str = None) -> int:
    """Infer section level based on content and context."""
    # Main section headers are typically standard names
    main_headers = [
        "IAS ",
        "IFRS ",
        "FRS ",
        "UK exit",
        "Periodic Review",
        "Effective date"
    ]
    
    # Check if this is a main section
    if any(title.startswith(prefix) for prefix in main_headers):
        return 1
        
    # If previous title was a main section (e.g., "IAS 36"),
    # and this title relates to it, it's a subsection
    if prev_title and any(prev_title.startswith(prefix) for prefix in main_headers):
        if not any(title.startswith(prefix) for prefix in main_headers):
            return 2
            
    return 1  # Default level


def build_section_hierarchy(sections):
    """Build section hierarchy based on inferred structure."""
    hierarchy = []
    current_main_section = None
    prev_title = None
    
    for section in sections:
        # Infer the true level
        inferred_level = infer_section_level(section["title"], prev_title)
        section["level"] = inferred_level
        
        if inferred_level == 1:
            # This is a main section
            current_main_section = section
            current_main_section["subsections"] = []
            hierarchy.append(current_main_section)
        else:
            # This is a subsection
            if current_main_section:
                current_main_section["subsections"].append(section)
            else:
                # If no main section exists, treat it as a main section
                section["level"] = 1
                hierarchy.append(section)
        
        prev_title = section["title"]
    
    return hierarchy


def merge_consecutive_tables(content_items):
    """Merge consecutive tables that appear to be continuations."""
    if not content_items:
        return content_items
    
    merged_content = []
    current_table = None
    
    for item in content_items:
        if item["type"] == "table":
            # Check if this could be a continuation of previous table
            if current_table and item.get("rows") and current_table.get("rows"):
                # Compare headers (first row)
                current_headers = current_table["rows"][0]
                new_headers = item["rows"][0]
                
                if current_headers == new_headers:
                    # Merge tables - skip the header row of the second table
                    current_table["rows"].extend(item["rows"][1:])
                    continue
            
            # Not a continuation or no previous table
            if current_table:
                merged_content.append(current_table)
            current_table = item
        else:
            # Non-table item - add previous table if exists and then this item
            if current_table:
                merged_content.append(current_table)
                current_table = None
            merged_content.append(item)
    
    # Add final table if exists
    if current_table:
        merged_content.append(current_table)
    
    return merged_content


def simplify_document(doc) -> Dict[str, List[Dict[str, Any]]]:
    """Convert Docling document to simplified format while preserving structure."""
    # Collect sections first
    sections = []
    current_section = None
    
    # Process all text items in order
    for text in doc.texts:
        item_type = type(text).__name__
        
        if item_type == 'SectionHeaderItem':
            # Start a new section
            current_section = {
                "type": "section",
                "title": text.text,
                "content": []
            }
            sections.append(current_section)
            
        elif item_type == 'ListItem':
            # Extract paragraph number if present
            text_content = text.text
            paragraph_num = None
            
            # Try to extract paragraph number from start of text
            if text_content and text_content[0].isdigit():
                parts = text_content.split(' ', 1)
                if parts[0].isdigit():
                    paragraph_num = int(parts[0])
                    text_content = parts[1] if len(parts) > 1 else ''
            
            item = {
                "type": "paragraph",
                "text": text_content,
            }
            
            if paragraph_num is not None:
                item["number"] = paragraph_num
            
            # Handle sub-items (like (a), (b), etc.)
            if text.marker and text.marker.startswith('('):
                item["type"] = "sub_item"
                item["marker"] = text.marker
                
            # Add to current section if exists
            if current_section:
                current_section["content"].append(item)
                
        elif item_type == 'TextItem' and text.label == 'footnote':
            footnote = {
                "type": "footnote",
                "text": text.text
            }
            if current_section:
                current_section["content"].append(footnote)
    
    # Process tables
    for table in doc.tables:
        table_data = {
            "type": "table",
            "caption": table.captions[0].cref if table.captions else None,
            "rows": []
        }
        
        if hasattr(table.data, 'grid'):
            for row in table.data.grid:
                table_row = []
                for cell in row:
                    cell_text = getattr(cell, 'text', '') if cell else ''
                    table_row.append(cell_text)
                table_data["rows"].append(table_row)
        
        # Add to current section if exists
        if current_section:
            current_section["content"].append(table_data)
    
    # Build hierarchy from collected sections
    hierarchy = build_section_hierarchy(sections)
    
    # Process each section to merge consecutive tables
    for section in hierarchy:
        if section.get("content"):
            section["content"] = merge_consecutive_tables(section["content"])
        
        # Process subsections
        if section.get("subsections"):
            for subsection in section["subsections"]:
                if subsection.get("content"):
                    subsection["content"] = merge_consecutive_tables(subsection["content"])
    
    return {"document": hierarchy}


def process_pdf(pdf_path: str, output_path: str = None) -> None:
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
    
    result = doc_converter.convert(pdf_path)
    simplified_doc = simplify_document(result.document)
    
    # Determine output path
    if output_path is None:
        output_path = Path(pdf_path).with_suffix('.json')
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified_doc, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert.py <pdf_file>")
        sys.exit(1)
        
    source = sys.argv[1]
    process_pdf(source)
