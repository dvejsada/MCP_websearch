# Stage 1: Builder
FROM python:3.14-alpine as builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name "*.pyc" -delete && \
    find /opt/venv -type f -name "*.pyo" -delete


# Stage 2: Runtime
FROM python:3.14-alpine as runtime

WORKDIR /app

# Create non-root user for security
RUN adduser -D -s /bin/sh appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy application code (respects .dockerignore)
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port (adjust if needed)
EXPOSE 8000

# Run the FastMCP server
CMD ["python", "main.py"]

