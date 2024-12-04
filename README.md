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
python convert.py path/to/document.pdf
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

Convert a PDF file directly using the CLI:
```bash
python convert.py path/to/document.pdf
```

### REST API

Start the API server:
```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

#### API Endpoints

1. **Convert PDF Upload**
   - Endpoint: `POST /convert/upload`
   - Accepts multipart form data with a PDF file
   
   Example using curl:
   ```bash
   curl -X POST -F "file=@document.pdf" http://localhost:8000/convert/upload
   ```

2. **Convert PDF from URL**
   - Endpoint: `POST /convert/url`
   - Accepts a URL parameter pointing to a PDF file
   
   Example using curl:
   ```bash
   curl -X POST "http://localhost:8000/convert/url?url=http://example.com/document.pdf"
   ```

3. **Health Check**
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
                        [
                            "Header 1",
                            "Header 2"
                        ],
                        [
                            "Cell 1",
                            "Cell 2"
                        ]
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