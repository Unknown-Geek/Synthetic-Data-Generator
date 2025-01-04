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
        
        # Ensure output directory exists and is empty
        os.makedirs(self.output_dir, exist_ok=True)
        self._cleanup_output_directory()
        self.logger = self._setup_logging()

    def _cleanup_output_directory(self):
        """Remove all files in the output directory except .gitkeep"""
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

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("SyntheticDataPipeline")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        if logger.handlers:
            logger.handlers.clear()
            
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        log_file = os.path.join(self.output_dir, "pipeline.log")
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger

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
        epochs: int = 100
    ) -> pd.DataFrame:
        self.logger.info("Starting synthetic data generation")
        try:
            processed_data = data.copy()
            
            # Process only user-selected categorical columns and numeric columns
            all_columns = set(processed_data.columns)
            categorical_columns = set(self.categorical_columns)
            
            for col in all_columns:
                if col in categorical_columns:
                    # For categorical columns, convert to string type
                    processed_data[col] = processed_data[col].astype(str)
                elif self._is_numeric_column(processed_data, col):
                    # For numeric columns, convert and handle NaN values
                    processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
                    processed_data[col] = processed_data[col].fillna(processed_data[col].mean())
                else:
                    # Drop columns that are neither user-selected categorical nor numeric
                    self.logger.warning(f"Dropping column {col} - not selected as categorical and contains non-numeric data")
                    processed_data = processed_data.drop(columns=[col])

            self.logger.info(f"Processing columns. Selected categorical columns: {self.categorical_columns}")
            
            # Train CTGAN
            synthesizer = CTGAN(epochs=epochs)
            synthesizer.fit(processed_data, discrete_columns=self.categorical_columns)
            synthetic_data = synthesizer.sample(num_samples)
            
            self.logger.info(f"Generated {num_samples} synthetic samples")
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
        
        # Ensure all categorical columns exist in both dataframes
        missing_cols_real = set(self.categorical_columns) - set(real_data.columns)
        missing_cols_synth = set(self.categorical_columns) - set(synthetic_data.columns)
        
        if missing_cols_real or missing_cols_synth:
            self.logger.error(f"Missing columns in real data: {missing_cols_real}")
            self.logger.error(f"Missing columns in synthetic data: {missing_cols_synth}")
            raise ValueError("Not all categorical columns present in both datasets")
        
        # Filter both dataframes to only include existing categorical columns
        valid_categorical_columns = [
            col for col in self.categorical_columns 
            if col in real_data.columns and col in synthetic_data.columns
        ]
        
        metrics = {
            "real_shape": real_data[valid_categorical_columns].shape,
            "synthetic_shape": synthetic_data[valid_categorical_columns].shape,
            "column_match": sorted(valid_categorical_columns) == sorted(self.categorical_columns),
            "basic_stats": {}
        }
        
        # Only validate categorical columns that exist in both datasets
        for col in valid_categorical_columns:
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

    def run_pipeline(self, num_samples: int = 1000) -> None:
        try:
            real_data = self.load_data()
            synthetic_data = self.generate_synthetic_data(real_data, num_samples)
            validation_metrics = self.validate_synthetic_data(real_data, synthetic_data)
            self.save_outputs(synthetic_data, validation_metrics)
            self.logger.info("Pipeline completed successfully")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise