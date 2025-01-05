# app.py
import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import traceback
import logging
import shutil
from synthetic_data_pipeline import SyntheticDataPipeline
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Setup CORS with Render domains
CORS(app, origins="*", supports_credentials=True)

app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/generate', methods=['POST'])
def generate_synthetic_data():
    try:
        # Clean up output directory before starting
        cleanup_output_directory(app.config['OUTPUT_FOLDER'])
        logger.info("Cleaned up output directory")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        logger.info(f"File saved to {filepath}")

        # Get configuration from request
        config = request.form.to_dict()
        categorical_columns = [
            col.strip() 
            for col in config.get('categorical_columns', '').replace('"', '').replace("'", '').split(',')
            if col.strip()
        ]
        
        if not categorical_columns:
            return jsonify({'error': 'No valid categorical columns provided'}), 400
            
        try:
            num_samples = int(config.get('num_samples', 1000))
        except ValueError:
            return jsonify({'error': 'Invalid number of samples'}), 400

        logger.info(f"Processing with categorical columns: {categorical_columns}")
        logger.info(f"Number of samples requested: {num_samples}")

        # Run pipeline with kwargs
        pipeline = SyntheticDataPipeline(
            input_file=filepath,
            categorical_columns=categorical_columns,
            output_dir=os.path.abspath(app.config['OUTPUT_FOLDER'])
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
        
        # Clean up
        os.remove(filepath)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='synthetic_data.csv'
        )

    except Exception as e:
        logger.error(f"Error in generate_synthetic_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use Render's PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)