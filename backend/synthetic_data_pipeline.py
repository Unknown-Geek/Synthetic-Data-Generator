# synthetic_data_pipeline.py
import pandas as pd
import numpy as np
from ctgan.synthesizers.ctgan import CTGAN
from sklearn.model_selection import train_test_split
import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional
import shutil
import tempfile

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

    def generate_synthetic_data(
        self,
        data: pd.DataFrame,
        num_samples: int = 1000,
        epochs: int = 50,  # Reduced epochs
        chunk_size: int = 1000  # Smaller chunks
    ) -> pd.DataFrame:
        self.logger.info("Starting synthetic data generation")
        try:
            processed_data = data.copy()
            
            # Reduce memory usage by converting to smaller dtypes
            for col in processed_data.columns:
                if processed_data[col].dtype == 'int64':
                    processed_data[col] = processed_data[col].astype('int32')
                elif processed_data[col].dtype == 'float64':
                    processed_data[col] = processed_data[col].astype('float32')
                elif processed_data[col].dtype == 'object':
                    processed_data[col] = processed_data[col].astype('category')

            # Process in smaller batches
            synthetic_pieces = []
            samples_per_chunk = max(1, num_samples // (len(processed_data) // chunk_size))
            
            for start in range(0, len(processed_data), chunk_size):
                end = min(start + chunk_size, len(processed_data))
                chunk = processed_data[start:end]
                
                # Use a more memory-efficient configuration for CTGAN
                synthesizer = CTGAN(
                    epochs=epochs,
                    batch_size=min(100, len(chunk)),
                    generator_dim=(64, 64),  # Smaller network
                    discriminator_dim=(64, 64)  # Smaller network
                )
                
                synthesizer.fit(chunk, discrete_columns=self.categorical_columns)
                synthetic_chunk = synthesizer.sample(samples_per_chunk)
                synthetic_pieces.append(synthetic_chunk)
                
                # Clear memory
                del synthesizer
                import gc
                gc.collect()
                
                self.logger.info(f"Processed chunk {start} to {end}")

            # Combine all pieces
            synthetic_data = pd.concat(synthetic_pieces, ignore_index=True)
            if len(synthetic_data) > num_samples:
                synthetic_data = synthetic_data.sample(n=num_samples)
            
            self.logger.info(f"Generated {len(synthetic_data)} synthetic samples")
            return synthetic_data
            
        except Exception as e:
            self.logger.error(f"Error generating synthetic data: {str(e)}")
            raise

    def validate_synthetic_data(
        self,
        real_data: pd.DataFrame,
        synthetic_data: pd.DataFrame
    ) -> Dict:
        """Validate synthetic data against real data for specified categorical columns."""
        self.logger.info("Validating synthetic data")
        
        # Validate column existence
        missing_cols = []
        for col in self.categorical_columns:
            if col not in real_data.columns:
                missing_cols.append(f"'{col}' missing in real data")
            if col not in synthetic_data.columns:
                missing_cols.append(f"'{col}' missing in synthetic data")
        
        if missing_cols:
            error_msg = "Missing columns: " + ", ".join(missing_cols)
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Only validate columns that exist in both datasets
        metrics = {
            "real_shape": (len(real_data), len(self.categorical_columns)),
            "synthetic_shape": (len(synthetic_data), len(self.categorical_columns)),
            "column_match": True,  # We validated this above
            "basic_stats": {}
        }
        
        # Calculate statistics for each categorical column
        for col in self.categorical_columns:
            metrics["basic_stats"][col] = {
                "unique_values_real": real_data[col].nunique(),
                "unique_values_synthetic": synthetic_data[col].nunique()
            }
            
        return metrics

    def save_outputs(
        self,
        synthetic_data: pd.DataFrame,
        validation_metrics: Dict
    ) -> None:
        """Save synthetic data and metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter only categorical columns for output
        output_data = synthetic_data[self.categorical_columns].copy()
        
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

    def run_pipeline(self, num_samples: int = 1000, chunk_size: int = 10000, **kwargs) -> None:
        """
        Run the synthetic data generation pipeline.
        
        Args:
            num_samples: Number of synthetic samples to generate
            **kwargs: Additional arguments passed to generate_synthetic_data
        """
        try:
            real_data = self.load_data()
            synthetic_data = self.generate_synthetic_data(real_data, num_samples=num_samples, chunk_size=chunk_size, **kwargs)
            validation_metrics = self.validate_synthetic_data(real_data, synthetic_data)
            self.save_outputs(synthetic_data, validation_metrics)
            self.logger.info("Pipeline completed successfully")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise