import asyncio
import json
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from recipes.registry import registry

# Global variable to store the converter
doc_converter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application"""
    global doc_converter
    
    # Initialize converter with options
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
    
    # Warm up the models by processing a small sample PDF
    try:
        # Create a minimal PDF file for warmup
        sample_path = Path("warmup.pdf")
        if not sample_path.exists():
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(str(sample_path))
            c.drawString(100, 750, "Warmup document")
            c.save()
        
        # Process it to load models
        _ = doc_converter.convert(str(sample_path))
        
        # Clean up
        os.unlink(str(sample_path))
        
        print("Models loaded successfully")
    except Exception as e:
        print(f"Warning: Model warmup failed: {e}")
        # Continue anyway - models will load on first request
    
    yield  # Server is running
    
    # Cleanup (if needed) when server shuts down
    if sample_path.exists():
        os.unlink(str(sample_path))

app = FastAPI(
    title="PDF to JSON Converter API",
    description="Convert PDF documents to structured JSON format",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def get_viewer():
    """Serve the JSON viewer interface"""
    return FileResponse('json-viewer.html')

@app.post("/convert/upload")
async def convert_uploaded_pdf(file: UploadFile, recipe: str = "default"):
    """Convert an uploaded PDF file to JSON using specified recipe"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Create temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Get the requested recipe
        conversion_recipe = registry.get_recipe(recipe)
        
        # Process the PDF
        result = doc_converter.convert(tmp_path)
        simplified_doc = conversion_recipe.simplify_document(result.document)
        
        # Clean up
        os.unlink(tmp_path)
        
        return JSONResponse(content=simplified_doc)
        
    except Exception as e:
        # Clean up on error
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert/url")
async def convert_pdf_from_url(url: str, recipe: str = "default"):
    """Convert a PDF from a URL to JSON using specified recipe"""
    if not url.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="URL must point to a PDF file")
    
    try:
        # Download the PDF
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to download PDF")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
        
        # Get the requested recipe
        conversion_recipe = registry.get_recipe(recipe)
        
        # Process the PDF
        result = doc_converter.convert(tmp_path)
        simplified_doc = conversion_recipe.simplify_document(result.document)
        
        # Clean up
        os.unlink(tmp_path)
        
        return JSONResponse(content=simplified_doc)
        
    except Exception as e:
        # Clean up on error
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/recipes")
async def list_recipes():
    """List all available conversion recipes"""
    return {
        "recipes": [
            {
                "name": name,
                "description": registry.get_recipe(name).__class__.__doc__ or ""
            }
            for name in registry.list_recipes()
        ]
    }

@app.get("/demo")
@app.post("/demo")
async def demo_endpoint(time: int = 0):
    """Demo endpoint that sleeps for specified seconds and returns sample JSON"""
    # Sleep for requested duration
    await asyncio.sleep(time)
    
    # Load and return the sample JSON
    sample_path = Path("amnesty-example-2.json")
    with open(sample_path) as f:
        return json.load(f)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 