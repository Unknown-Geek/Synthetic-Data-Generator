import pandas as pd
import numpy as np
from ctgan import CTGAN
from sklearn.model_selection import train_test_split
import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional
import shutil
import tempfile

# Check pandas version
logger = logging.getLogger(__name__)
logger.info(f"Using pandas version: {pd.__version__}")

class SyntheticDataPipeline:
    def __init__(
        self,
        input_file: str,
        categorical_columns: List[str],
        output_dir: str = "output",
        metadata: Dict = None
    ):
        self.input_file = input_file
        self.categorical_columns = categorical_columns
        self.output_dir = os.path.abspath(output_dir)
        self.metadata = metadata or {}
        self.logger = None
        
        # Ensure output directory exists and is empty
        os.makedirs(self.output_dir, exist_ok=True)
        self._cleanup_output_directory()
        self._setup_logging()

    def _cleanup_output_directory(self):
        """Remove all files in the output directory except .gitkeep"""
        # Close logging handlers before cleanup
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
            self.logger.handlers.clear()

        for filename in os.listdir(self.output_dir):
            if filename != '.gitkeep':
                file_path = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Error deleting {file_path}: {e}')

    def _setup_logging(self) -> None:
        """Setup logging with a temporary log file."""
        self.logger = logging.getLogger("SyntheticDataPipeline")
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        if self.logger.handlers:
            for handler in self.logger.handlers:
                handler.close()
            self.logger.handlers.clear()
            
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Use a temporary directory for the log file
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "pipeline.log")
        
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def load_data(self) -> pd.DataFrame:
        self.logger.info(f"Loading data from {self.input_file}")
        try:
            data = pd.read_csv(self.input_file)
            self.logger.info(f"Loaded {len(data)} rows of data")
            return data
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def _is_numeric_column(self, data: pd.DataFrame, column: str) -> bool:
        """Check if a column is numeric."""
        try:
            pd.to_numeric(data[column])
            return True
        except (ValueError, TypeError):
            return False

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data by properly handling types and missing values"""
        processed_data = data.copy()
        
        # Only process and return user-selected categorical columns
        selected_data = processed_data[self.categorical_columns].copy()
        
        # Handle categorical columns
        for col in self.categorical_columns:
            # Convert to string and handle missing values
            selected_data[col] = selected_data[col].fillna('MISSING')
            selected_data[col] = selected_data[col].astype(str)
        
        self.logger.info(f"Preprocessed {len(self.categorical_columns)} categorical columns")
        return selected_data

    def generate_synthetic_data(self, data: pd.DataFrame, num_samples: int = 1000, epochs: int = 100, chunk_size: int = 1000) -> pd.DataFrame:
        """Generate synthetic data using CTGAN"""
        self.logger.info("Starting synthetic data generation")
        try:
            # Only process selected categorical columns
            processed_data = self.preprocess_data(data)
            
            # Initialize CTGAN with conservative parameters
            synthesizer = CTGAN(
                epochs=epochs,
                batch_size=500,
                generator_dim=(128, 128),
                discriminator_dim=(128, 128),
                embedding_dim=128,
                verbose=True
            )

            # Fit the model with all columns as discrete
            self.logger.info("Training CTGAN model...")
            synthesizer.fit(processed_data, discrete_columns=self.categorical_columns)

            # Generate synthetic data
            self.logger.info(f"Generating {num_samples} synthetic samples...")
            synthetic_data = synthesizer.sample(num_samples)

            # Post-process to ensure string type and handle missing values
            for col in self.categorical_columns:
                synthetic_data[col] = synthetic_data[col].astype(str)
                synthetic_data[col] = synthetic_data[col].replace('MISSING', np.nan)

            self.logger.info(f"Generated {len(synthetic_data)} synthetic samples")
            return synthetic_data

        except Exception as e:
            self.logger.error(f"Error in generate_synthetic_data: {str(e)}")
            raise

    def validate_synthetic_data(self, real_data: pd.DataFrame, synthetic_data: pd.DataFrame) -> Dict:
        """Validate synthetic data against real data for specified categorical columns."""
        self.logger.info("Validating synthetic data")
        
        metrics = {
            "real_shape": real_data.shape,
            "synthetic_shape": synthetic_data.shape,
            "column_match": all(col in synthetic_data.columns for col in real_data.columns),
            "basic_stats": {}
        }
        
        for col in self.categorical_columns:
            if col in real_data.columns and col in synthetic_data.columns:
                metrics["basic_stats"][col] = {
                    "unique_values_real": real_data[col].nunique(),
                    "unique_values_synthetic": synthetic_data[col].nunique()
                }
        
        return metrics

    def save_outputs(self, synthetic_data: pd.DataFrame, validation_metrics: Dict) -> None:
        """Save synthetic data and metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter only the user-selected categorical columns
        output_data = synthetic_data[self.categorical_columns].copy()
        self.logger.info(f"Saving {len(self.categorical_columns)} categorical columns: {', '.join(self.categorical_columns)}")
        
        # Save filtered data
        output_file = os.path.join(self.output_dir, f"synthetic_data_{timestamp}.csv")
        output_data.to_csv(output_file, index=False)
        
        metadata = {
            "generation_timestamp": timestamp,
            "original_file": self.input_file,
            "num_samples": len(output_data),
            "categorical_columns": self.categorical_columns,
            "validation_metrics": validation_metrics,
            **self.metadata
        }
        
        metadata_file = os.path.join(self.output_dir, f"metadata_{timestamp}.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Saved synthetic data to {output_file}")
        self.logger.info(f"Saved metadata to {metadata_file}")

    def create_metadata_file(self, synthetic_data: pd.DataFrame, timestamp: str) -> None:
        """Create a metadata.json file with dataset details."""
        metadata = {
            "name": "Synthetic Healthcare Dataset",
            "description": "A privacy-preserving synthetic dataset for healthcare analysis.",
            "columns": [
                {"name": col, "type": "categorical"} for col in self.categorical_columns
            ],
            "size": f"{len(synthetic_data)} rows"
        }
        metadata_file = os.path.join(self.output_dir, f"metadata_{timestamp}.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        self.logger.info(f"Saved metadata to {metadata_file}")

    def compress_files(self, timestamp: str) -> None:
        """Compress the dataset and documentation into a zip file."""
        zip_filename = os.path.join(self.output_dir, f"dataset_package_{timestamp}.zip")
        shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', self.output_dir)
        self.logger.info(f"Compressed files into {zip_filename}")

    def run_pipeline(self, num_samples: int = 1000, chunk_size: int = 10000, epochs: int = 100, **kwargs) -> None:
        """Run the synthetic data generation pipeline."""
        try:
            real_data = self.load_data()
            synthetic_data = self.generate_synthetic_data(real_data, num_samples=num_samples, epochs=epochs, chunk_size=chunk_size, **kwargs)
            validation_metrics = self.validate_synthetic_data(real_data, synthetic_data)
            self.save_outputs(synthetic_data, validation_metrics)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.create_metadata_file(synthetic_data, timestamp)
            self.compress_files(timestamp)
            self.logger.info("Pipeline completed successfully")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise