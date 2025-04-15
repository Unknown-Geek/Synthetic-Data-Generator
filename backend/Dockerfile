# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir pandas && \
    pip install --no-cache-dir torch && \
    pip install --no-cache-dir -r requirements.txt

# Make sure directories exist for file operations
RUN mkdir -p temp_uploads output

# Set production environment
ENV ENVIRONMENT=production
# Default to 2 workers per core for HF Spaces (2 vCPUs, 16GB RAM)
ENV WORKERS_PER_CORE=2
# Set a longer timeout for synthetic data generation
ENV TIMEOUT=300

COPY --chown=user . /app
# Use our new startup script instead of directly calling uvicorn
CMD ["python", "start_server.py"]
