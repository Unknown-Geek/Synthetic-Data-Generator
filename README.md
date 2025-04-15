---
title: Synthetic Data Generator
emoji: 🧪
colorFrom: blue
colorTo: green
sdk: gradio
app_file: backend/app.py
pinned: false
license: mit
---

# Synthetic Data Generator

A web application that generates synthetic data from CSV files while preserving statistical properties and privacy. The application uses CTGAN (Conditional Tabular GAN) to generate realistic synthetic data from categorical columns.

## Features

- Upload CSV files and select categorical columns
- Generate synthetic data with customizable sample size
- Download synthetic data in CSV format
- Real-time progress tracking
- Automatic validation of generated data
- Metadata generation for each dataset
- Server health monitoring with fallback mechanism

## Architecture

The project consists of two main components:

### Frontend

- Built with React.js and TailwindCSS
- Features a modern glassmorphism UI design
- Real-time server status monitoring with fallback capability
- Interactive column selection
- Progress tracking during generation
- Responsive design with Framer Motion animations

### Backend

- FastAPI-based REST API (with Flask compatibility layer)
- CTGAN implementation for synthetic data generation
- Automatic data validation and preprocessing
- File handling and cleanup
- Comprehensive logging and error handling
- Docker containerization for easy deployment

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- pip (Python package manager)
- npm (Node.js package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd synthetic-data-generator
```

2. Set up the backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:

```bash
cd frontend
npm install
npm run build:css  # Generate the Tailwind CSS output
```

### Alternatively (For Windows)

1. Clone the repository:

```bash
git clone <repository-url>
cd synthetic-data-generator
```

2. Run the executable "run.bat" to directly run the application:

```bash
.\run.bat
```

## Configuration

1. Create or modify the `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://localhost:7860
REACT_APP_PRODUCTION_API_URL=https://mojo-maniac-synthetic-data-generator-backend.hf.space
NODE_ENV=production
NODE_OPTIONS=--openssl-legacy-provider
```

2. Create a `.env` file in the backend directory if needed for custom configuration.

## Running the Application

1. Start the backend server:

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:7860`

2. Start the frontend development server:

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open the application in your browser
2. Upload a CSV file using the file upload interface
3. Select the categorical columns you want to generate synthetic data for
4. Specify the number of samples to generate
5. Click "Generate" and wait for the process to complete
6. Download the generated synthetic data file

## File Structure

```
.
├── backend/
│   ├── app.py                     # FastAPI server and main API endpoints
│   ├── main.py                    # Flask compatibility layer
│   ├── synthetic_data_pipeline.py # Core data generation logic
│   ├── synthetic_data_pipeline.ipynb # Notebook for experimentation
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container configuration for deployment
│   ├── output/                    # Generated data output directory
│   ├── temp_uploads/              # Temporary storage for uploaded files
│   └── README.md                  # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── utils/                 # Utility functions
│   │   ├── ApiContext.js          # API context with fallback mechanism
│   │   ├── UploadForm.jsx         # Main form component
│   │   ├── index.js               # Application entry point
│   │   ├── site.css               # Tailwind source CSS
│   │   └── output.css             # Generated Tailwind CSS
│   ├── public/                    # Static files
│   ├── package.json               # Node.js dependencies
│   └── .env                       # Environment configuration
├── run.bat                        # Windows one-click setup and run script
└── README.md                      # Project documentation
```

## API Endpoints

- `GET /health` - Check server status
- `POST /generate` - Generate synthetic data
  - Request: Multipart form data with:
    - file: CSV file
    - categorical_columns: Comma-separated column names
    - num_samples: Number of samples to generate

## Error Handling

The application includes comprehensive error handling for:

- Invalid file formats
- Missing or invalid columns
- Server connectivity issues with automatic fallback
- Generation process failures
- Progress tracking and cancellation

## Deployment

The application is designed for easy deployment:

- The backend is containerized using Docker
- The frontend can be deployed to static hosting services
- Configuration supports both development and production environments
- Built-in server health checking and fallback mechanisms

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
