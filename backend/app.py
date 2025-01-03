# app.py
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from synthetic_data_pipeline import SyntheticDataPipeline

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/generate', methods=['POST'])
def generate_synthetic_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get configuration from request
        config = request.form.to_dict()
        categorical_columns = config.get('categorical_columns', '').split(',')
        num_samples = int(config.get('num_samples', 1000))
        metadata = config.get('metadata', {})

        # Run pipeline
        pipeline = SyntheticDataPipeline(
            input_file=filepath,
            categorical_columns=categorical_columns,
            metadata=metadata
        )
        pipeline.run_pipeline(num_samples=num_samples)

        # Get latest generated file
        output_dir = pipeline.output_dir
        files = [f for f in os.listdir(output_dir) if f.startswith("synthetic_data_")]
        latest_file = sorted(files)[-1]
        
        # Clean up
        os.remove(filepath)
        
        return send_file(
            os.path.join(output_dir, latest_file),
            as_attachment=True,
            download_name='synthetic_data.csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)