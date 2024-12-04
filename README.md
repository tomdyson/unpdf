# unPDF

Convert PDF documents into structured JSON. unPDF extracts headings, sections, paragraphs, tables, and maintains document hierarchy.

## Features

- Converts PDF documents to structured JSON
- Maintains document hierarchy and section relationships
- Handles tables, footnotes, and nested content
- Provides both CLI and REST API interfaces
- Intelligent section level inference
- Table continuation detection and merging
- Web interface for viewing converted documents
- Multiple conversion recipes for different document types

## Quick Start

```bash
# Clone the repository
git clone https://github.com/tomdyson/unpdf.git
cd unpdf

# Install dependencies with uv
uv venv
source .venv/bin/activate  # or `.venv/Scripts/activate` on Windows
uv pip install -e .

# Run the API
uvicorn api:app --reload

# Or use the CLI
python unpdf.py path/to/document.pdf
```

Visit http://localhost:8000 for the web interface, or http://localhost:8000/docs for the API documentation.

## Development Setup

Requirements:
- Python 3.12+
- uv (recommended) or pip

```bash
# Install uv if you haven't already
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # or `.venv/Scripts/activate` on Windows

# Install dependencies
uv pip install -e .
```

## Usage

### Command Line Interface

Convert a PDF file using the CLI:
```bash
python unpdf.py path/to/document.pdf
```

You can specify a conversion recipe for different document types:
```bash
python unpdf.py path/to/document.pdf --recipe frc     # Financial Reporting Council documents
python unpdf.py path/to/document.pdf --recipe amnesty # Amnesty International documents
```

Available recipes:
- `default`: Standard conversion (inherits from FRC recipe)
- `frc`: Optimized for Financial Reporting Council documents
- `amnesty`: Optimized for Amnesty International documents, handles repeated headers

### REST API

Start the API server:
```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

#### API Endpoints

1. **List Available Recipes**
   - Endpoint: `GET /recipes`
   - Returns list of available conversion recipes and their descriptions
   
   Example using curl:
   ```bash
   curl http://localhost:8000/recipes
   ```
   
   Example response:
   ```json
   {
     "recipes": [
       {
         "name": "default",
         "description": "Default conversion recipe that inherits FRC document processing behavior."
       },
       {
         "name": "frc",
         "description": "Recipe optimized for Financial Reporting Council (FRC) documents."
       },
       {
         "name": "amnesty",
         "description": "Recipe optimized for Amnesty International documents."
       }
     ]
   }
   ```

2. **Convert PDF Upload**
   - Endpoint: `POST /convert/upload`
   - Accepts multipart form data with a PDF file
   - Optional `recipe` query parameter to specify conversion recipe
   
   Example using curl:
   ```bash
   # Basic conversion
   curl -X POST -F "file=@document.pdf" http://localhost:8000/convert/upload

   # Using specific recipe
   curl -X POST -F "file=@document.pdf" "http://localhost:8000/convert/upload?recipe=frc"
   ```

3. **Convert PDF from URL**
   - Endpoint: `POST /convert/url`
   - Accepts a URL parameter pointing to a PDF file
   - Optional `recipe` query parameter to specify conversion recipe
   
   Example using curl:
   ```bash
   curl -X POST "http://localhost:8000/convert/url?url=http://example.com/document.pdf&recipe=amnesty"
   ```

4. **Health Check**
   - Endpoint: `GET /health`
   - Returns API health status

## Output Format

The converter produces JSON with the following structure:

```json
{
    "document": [
        {
            "type": "section",
            "title": "Section Title",
            "level": 1,
            "content": [
                {
                    "type": "paragraph",
                    "text": "Paragraph content",
                    "number": 1
                },
                {
                    "type": "table",
                    "caption": "Table Caption",
                    "rows": [
                        ["Header 1", "Header 2"],
                        ["Cell 1", "Cell 2"]
                    ]
                }
            ],
            "subsections": [
                {
                    "type": "section",
                    "title": "Subsection Title",
                    "level": 2,
                    "content": []
                }
            ]
        }
    ]
}
```

## Features in Detail

### Conversion Recipes
- Pluggable system for different document types
- Each recipe can implement custom processing logic
- Easy to add new recipes for specific document formats
- Built-in recipes for common document types

### Section Hierarchy
- Automatically detects section levels
- Maintains parent-child relationships
- Supports multiple hierarchy levels

### Content Processing
- Extracts and numbers paragraphs
- Identifies and processes sub-items (e.g., (a), (b), etc.)
- Handles footnotes
- Processes and merges related tables

### Table Handling
- Detects and extracts tables
- Merges split tables that span multiple pages
- Preserves table structure and formatting

## Creating Custom Recipes

You can create custom recipes for specific document types:

1. Create a new file in the `recipes` directory
2. Inherit from `ConversionRecipe` base class
3. Implement the `simplify_document` method
4. Register the recipe in `recipes/registry.py`

Example:
```python
from typing import Any, Dict, List
from .base import ConversionRecipe

class CustomRecipe(ConversionRecipe):
    """Recipe for custom document format."""
    
    def simplify_document(self, doc) -> Dict[str, List[Dict[str, Any]]]:
        # Implement custom conversion logic
        pass
```

## Dependencies

- fastapi: Web framework for the API
- python-multipart: File upload handling
- httpx: Async HTTP client for URL processing
- uvicorn: ASGI server
- docling: Document processing library

## Deployment

### Docker

Build the Docker image:
```bash
docker build -t pdf-converter .
```

Run the container:
```bash
docker run -p 8000:8000 pdf-converter
```

### Coolify

1. Create a new service in Coolify
2. Select "Docker" as the deployment method
3. Connect your repository
4. Configure the following:
    - Build Command: `docker build -t pdf-converter .`
    - Port: 8000
    - Health Check Path: `/health`
5. Deploy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)