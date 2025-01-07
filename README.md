# Synthetic Data Generator

A web application that generates synthetic data from CSV files while preserving statistical properties and privacy. The application uses CTGAN (Conditional Tabular GAN) to generate realistic synthetic data from categorical columns.

## Features

- Upload CSV files and select categorical columns
- Generate synthetic data with customizable sample size
- Download synthetic data in CSV format
- Real-time progress tracking
- Automatic validation of generated data
- Metadata generation for each dataset

## Architecture

The project consists of two main components:

### Frontend
- Built with React.js and TailwindCSS
- Features a modern glassmorphism UI design
- Real-time server status monitoring
- Interactive column selection
- Progress tracking during generation

### Backend
- Flask-based REST API
- CTGAN implementation for synthetic data generation
- Automatic data validation and preprocessing
- File handling and cleanup
- Logging and error handling

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

1. Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8080
```

2. Create a `.env` file in the backend directory if needed for custom configuration.

## Running the Application

1. Start the backend server:
```bash
cd backend
python app.py
```
The backend will run on `http://localhost:8080`

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
│   ├── app.py                 # Flask server and API endpoints
│   ├── synthetic_data_pipeline.py  # Core data generation logic
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Backend documentation
├── frontend/
│   ├── src/                  # React source files
│   ├── public/               # Static files
│   ├── package.json          # Node.js dependencies
│   └── .env                  # Environment configuration
└── README.md                 # Project documentation
```

## API Endpoints

- `GET /health` - Check server status
- `POST /generate` - Generate synthetic data
  - Request: Multipart form data with:
    - 

file

: CSV file
    - 

categorical_columns

: Comma-separated column names
    - 

num_samples

: Number of samples to generate

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Missing or invalid columns
- Server connectivity issues
- Generation process failures

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
