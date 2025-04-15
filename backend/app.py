import os
import sys
import logging

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Check versions before importing other libraries
    import numpy as np
    import pandas as pd
    logger.info(f"NumPy version: {np.__version__}")
    logger.info(f"Pandas version: {pd.__version__}")
    
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
    except ImportError as e:
        logger.warning(f"PyTorch import error: {str(e)}")
    
    from fastapi import FastAPI, UploadFile, File, Form
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import traceback
    import shutil
    import tempfile
    import uvicorn  # Import uvicorn for running the server
    
    try:
        from synthetic_data_pipeline import SyntheticDataPipeline
        import time
    except ImportError as e:
        logger.error(f"Failed to import SyntheticDataPipeline: {str(e)}")
        raise
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    logger.error("Try checking package compatibility or downgrading packages")
    sys.exit(1)

app = FastAPI(title="Synthetic Data Generator")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'output'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def cleanup_output_directory(directory):
    """Remove all files in the output directory except .gitkeep"""
    for filename in os.listdir(directory):
        if filename != '.gitkeep':
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    # Add retry logic for locked files
                    max_retries = 3
                    for _ in range(max_retries):
                        try:
                            os.unlink(file_path)
                            break
                        except PermissionError:
                            time.sleep(1)  # Wait before retry
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except Exception as e:
                logger.error(f'Error deleting {file_path}: {e}')

@app.get("/")
def root():
    return {"message": "Synthetic Data Generator API", "numpy_version": np.__version__}

@app.get("/health")
def health_check():
    try:
        return {"status": "healthy", "numpy_version": np.__version__}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/generate")
async def generate_synthetic_data(
    file: UploadFile = File(...),
    categorical_columns: str = Form(...),
    num_samples: int = Form(1000)
):
    try:
        # Clean up output directory before starting
        cleanup_output_directory(OUTPUT_FOLDER)
        logger.info("Cleaned up output directory")

        # Save uploaded file to temp location
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        try:
            contents = await file.read()
            temp_file.write(contents)
            temp_file.close()
            filepath = temp_file.name
            
            logger.info(f"File saved to {filepath}")
            
            # Parse categorical columns
            categorical_columns_list = [
                col.strip() 
                for col in categorical_columns.replace('"', '').replace("'", '').split(',')
                if col.strip()
            ]
            
            if not categorical_columns_list:
                return JSONResponse(
                    status_code=400,
                    content={"error": "No valid categorical columns provided"}
                )
            
            logger.info(f"Processing with categorical columns: {categorical_columns_list}")
            logger.info(f"Number of samples requested: {num_samples}")
            
            # Run pipeline with kwargs
            pipeline = SyntheticDataPipeline(
                input_file=filepath,
                categorical_columns=categorical_columns_list,
                output_dir=os.path.abspath(OUTPUT_FOLDER)
            )
            
            pipeline.run_pipeline(
                num_samples=num_samples,
                epochs=100,
                chunk_size=10000
            )
            
            # Get latest generated file
            output_dir = pipeline.output_dir
            files = [f for f in os.listdir(output_dir) if f.startswith("synthetic_data_")]
            
            if not files:
                raise Exception("No output file generated")
                
            latest_file = sorted(files)[-1]
            output_path = os.path.join(output_dir, latest_file)
            
            logger.info(f"Sending file: {output_path}")
            
            return FileResponse(
                path=output_path,
                filename="synthetic_data.csv",
                media_type="text/csv"
            )
        finally:
            # Clean up temp file
            if os.path.exists(filepath):
                os.unlink(filepath)

    except Exception as e:
        logger.error(f"Error in generate_synthetic_data: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Add this section to run the server when the script is executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting FastAPI server on port {port}")
    
    # Check if we should use the new startup script
    if os.path.exists("start_server.py"):
        logger.info("Using start_server.py for optimal server configuration")
        # For legacy compatibility, default to development mode when run directly
        os.environ["ENVIRONMENT"] = os.environ.get("ENVIRONMENT", "development")
        import importlib.util
        spec = importlib.util.spec_from_file_location("start_server", "start_server.py")
        start_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(start_server)
    else:
        # Fallback to direct uvicorn for backward compatibility
        logger.info("Using direct uvicorn server (legacy mode)")
        import uvicorn
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
