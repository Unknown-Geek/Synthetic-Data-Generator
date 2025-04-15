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

## Deployment

The backend is deployed on Hugging Face Spaces at:
https://mojo-maniac-synthetic-data-generator-backend.hf.space

## Frontend

The frontend application is available at:
[Synthetic Data Generator Frontend](https://github.com/yourusername/synthetic-data-generator-frontend)

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
