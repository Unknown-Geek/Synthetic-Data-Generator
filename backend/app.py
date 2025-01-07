import gradio as gr
import pandas as pd
import os
import shutil
from synthetic_data_pipeline import SyntheticDataPipeline

def generate_synthetic_data(file, categorical_columns, num_samples):
    try:
        # Save uploaded file
        filename = file.name
        filepath = os.path.join('temp_uploads', filename)
        with open(filepath, 'wb') as f:
            f.write(file.read())

        # Process categorical columns
        categorical_columns = [col.strip() for col in categorical_columns.split(',') if col.strip()]

        # Run pipeline
        pipeline = SyntheticDataPipeline(
            input_file=filepath,
            categorical_columns=categorical_columns,
            output_dir=os.path.abspath('output')
        )
        pipeline.run_pipeline(num_samples=int(num_samples), epochs=100, chunk_size=10000)

        # Get latest generated file
        output_dir = pipeline.output_dir
        files = [f for f in os.listdir(output_dir) if f.startswith("synthetic_data_")]
        latest_file = sorted(files)[-1]
        output_path = os.path.join(output_dir, latest_file)

        # Read and return the generated synthetic data
        synthetic_data = pd.read_csv(output_path)
        return synthetic_data

    except Exception as e:
        return str(e)

# Create Gradio interface
iface = gr.Interface(
    fn=generate_synthetic_data,
    inputs=[
        gr.inputs.File(label="Upload CSV File"),
        gr.inputs.Textbox(label="Categorical Columns (comma-separated)"),
        gr.inputs.Number(label="Number of Samples", default=1000)
    ],
    outputs=gr.outputs.Dataframe(label="Synthetic Data"),
    title="Synthetic Data Generator",
    description="Upload a CSV file, specify categorical columns, and generate synthetic data."
)

if __name__ == "__main__":
    iface.launch()