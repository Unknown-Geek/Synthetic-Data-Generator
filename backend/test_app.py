import pytest
from app import app as flask_app
import pandas as pd
from synthetic_data_pipeline import SyntheticDataPipeline
import os

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200

def test_generate_synthetic_data():
    # Test parameters
    input_csv = "test_real_dataset.csv"
    output_csv = "test_synthetic_dataset.csv"
    categorical_columns = ['column1', 'column2']
    num_samples = 10  # Add this line
    
    # Create a small test dataset
    pd.DataFrame({
        'column1': ['A', 'B', 'A', 'B'],
        'column2': ['X', 'Y', 'X', 'Y'],
        'value': [1, 2, 3, 4]
    }).to_csv(input_csv, index=False)
    
    # Initialize pipeline
    pipeline = SyntheticDataPipeline(
        input_file=input_csv,
        categorical_columns=categorical_columns,
        output_dir='output'
    )
    
    # Run pipeline with num_samples
    pipeline.run_pipeline(num_samples=num_samples)
    
    assert os.path.exists(output_csv)
    
    # Clean up
    os.remove(input_csv)
    if os.path.exists(output_csv):
        os.remove(output_csv)
