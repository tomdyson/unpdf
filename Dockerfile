# Build stage
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set up working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY README.md .


# Install dependencies into a virtual environment
RUN uv venv
RUN . .venv/bin/activate && uv pip install -e .

# Runtime stage
FROM python:3.12-slim

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
WORKDIR /app
COPY amnesty-example-2.json .
COPY unpdf.py .
COPY api.py .
COPY json-viewer.html .
COPY recipes recipes/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 