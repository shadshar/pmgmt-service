FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN pip install --no-cache-dir pip==23.1.2 setuptools==68.0.0 wheel==0.40.0

# Copy requirements first to leverage Docker cache
COPY setup.py README.md ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY pmgmt_service ./pmgmt_service
COPY templates ./templates

# Create directory for database
RUN mkdir -p /data

# Set environment variables
ENV PMGMT_PORT=3716
ENV PMGMT_DB_PATH=/data/pmgmt.db

# Expose the application port
EXPOSE 3716

# Run the application
CMD ["python", "-m", "pmgmt_service.main"]