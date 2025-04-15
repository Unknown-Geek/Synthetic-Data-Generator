---
title: Synthetic Data Generator Backend
emoji: 🦀
colorFrom: indigo
colorTo: yellow
sdk: docker
pinned: false
---

# Synthetic Data Generator Backend

This is the backend server for the Synthetic Data Generator application. It provides the API for generating synthetic data from CSV files.

## API Endpoints

- `GET /health`: Check server status
- `POST /generate`: Generate synthetic data
  - Request: Multipart form data with:
    - file: CSV file
    - categorical_columns: Comma-separated column names
    - num_samples: Number of samples to generate

## Server Configuration

The backend now supports both development and production modes:

### Development Mode

Single-worker with hot reload for development:

```bash
cd backend
ENVIRONMENT=development python start_server.py
```

### Production Mode (Gunicorn with Uvicorn Workers)

Multi-worker configuration optimized for 2 vCPUs and 16GB RAM:

```bash
cd backend
python start_server.py
```

### Configuration Options

You can configure the server through environment variables:

- `ENVIRONMENT`: Set to "development" for hot reload, otherwise uses production mode
- `WORKERS_PER_CORE`: Workers per CPU core (default: 2 - optimized for 2 vCPUs)
- `WEB_CONCURRENCY`: Override total number of workers
- `PORT`: Server port (default: 7860)
- `TIMEOUT`: Request timeout in seconds (default: 300)

The server automatically adjusts worker and thread counts based on available CPU cores and memory.

## Deployment

The backend is deployed on Hugging Face Spaces at:
https://mojo-maniac-synthetic-data-generator-backend.hf.space

## Frontend

The frontend application is available at:
[Synthetic Data Generator Frontend](https://github.com/yourusername/synthetic-data-generator-frontend)

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
