"""
Gemini-powered Synthetic Data Generator

This module provides enhanced synthetic data generation using Google's Gemini API
combined with CTGAN for a hybrid approach that produces high-quality, realistic data.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for synthetic data generation."""
    use_gemini: bool = True
    gemini_batch_size: int = 50  # Rows per API call
    temperature: float = 0.8
    fallback_to_ctgan: bool = True


class GeminiSyntheticGenerator:
    """
    Hybrid synthetic data generator combining CTGAN + Gemini API.
    
    Strategy:
    1. CTGAN learns statistical distributions and column correlations
    2. Gemini enhances values with contextual understanding
    3. Falls back to CTGAN-only if Gemini unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client if API key is available."""
        if not self.api_key:
            logger.warning("No Gemini API key provided. Will use CTGAN-only mode.")
            return
        
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.0-flash"
            logger.info("Gemini client initialized successfully")
        except ImportError:
            logger.error("google-genai package not installed. Run: pip install google-genai")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        return self.client is not None
    
    def analyze_data_patterns(self, df: pd.DataFrame, categorical_columns: List[str]) -> Dict[str, Any]:
        """
        Analyze patterns in the original data to provide context for generation.
        """
        patterns = {
            "columns": categorical_columns,
            "row_count": len(df),
            "column_stats": {},
            "sample_rows": []
        }
        
        for col in categorical_columns:
            if col in df.columns:
                value_counts = df[col].value_counts()
                patterns["column_stats"][col] = {
                    "unique_values": df[col].nunique(),
                    "top_values": value_counts.head(10).to_dict(),
                    "sample_values": df[col].dropna().sample(min(5, len(df))).tolist()
                }
        
        # Get sample rows for context
        sample_size = min(10, len(df))
        patterns["sample_rows"] = df[categorical_columns].head(sample_size).to_dict('records')
        
        return patterns
    
    def _create_generation_prompt(
        self,
        patterns: Dict[str, Any],
        num_samples: int,
        ctgan_samples: Optional[pd.DataFrame] = None
    ) -> str:
        """Create a prompt for Gemini to generate synthetic data."""
        
        columns_info = []
        for col, stats in patterns["column_stats"].items():
            top_vals = list(stats["top_values"].keys())[:5]
            columns_info.append(f"- {col}: {stats['unique_values']} unique values, examples: {top_vals}")
        
        sample_rows_str = json.dumps(patterns["sample_rows"][:5], indent=2)
        
        prompt = f"""You are a synthetic data generator. Generate {num_samples} realistic synthetic data rows.

Dataset Context:
The data has these categorical columns:
{chr(10).join(columns_info)}

Sample rows from original data:
{sample_rows_str}

Instructions:
1. Generate exactly {num_samples} new, unique rows
2. Values should be realistic and contextually appropriate
3. Maintain similar distribution patterns as the original data
4. Create variety - avoid too many repeated values
5. Each row should be plausible given the column relationships

{"Reference structure from statistical model:" + chr(10) + ctgan_samples.head(5).to_json(orient='records') if ctgan_samples is not None else ""}

Return ONLY a JSON array of objects, where each object has these exact keys: {patterns['columns']}
Do not include any explanation or markdown formatting."""
        
        return prompt
    
    def _create_response_schema(self, columns: List[str]) -> Dict:
        """Create a JSON schema for structured output."""
        properties = {col: {"type": "string"} for col in columns}
        
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": properties,
                "required": columns
            }
        }
    
    def generate_with_gemini(
        self,
        patterns: Dict[str, Any],
        num_samples: int,
        ctgan_samples: Optional[pd.DataFrame] = None,
        config: Optional[GenerationConfig] = None
    ) -> pd.DataFrame:
        """
        Generate synthetic data using Gemini API with structured output.
        """
        if not self.is_available:
            raise RuntimeError("Gemini API not available")
        
        config = config or GenerationConfig()
        all_rows = []
        columns = patterns["columns"]
        
        # Generate in batches to handle large requests
        remaining = num_samples
        batch_num = 0
        
        while remaining > 0:
            batch_size = min(config.gemini_batch_size, remaining)
            batch_num += 1
            
            logger.info(f"Generating batch {batch_num}: {batch_size} samples")
            
            # Get corresponding CTGAN samples for this batch if available
            ctgan_batch = None
            if ctgan_samples is not None:
                start_idx = (batch_num - 1) * config.gemini_batch_size
                end_idx = start_idx + batch_size
                ctgan_batch = ctgan_samples.iloc[start_idx:end_idx]
            
            prompt = self._create_generation_prompt(patterns, batch_size, ctgan_batch)
            
            try:
                from google.genai import types
                
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=config.temperature,
                        response_mime_type="application/json",
                        response_schema=self._create_response_schema(columns)
                    )
                )
                
                # Parse JSON response
                batch_data = json.loads(response.text)
                all_rows.extend(batch_data)
                remaining -= batch_size
                
            except Exception as e:
                logger.error(f"Gemini generation error in batch {batch_num}: {e}")
                if config.fallback_to_ctgan and ctgan_samples is not None:
                    # Use CTGAN samples for failed batch
                    logger.info("Falling back to CTGAN samples for this batch")
                    all_rows.extend(ctgan_batch.to_dict('records'))
                    remaining -= batch_size
                else:
                    raise
        
        return pd.DataFrame(all_rows[:num_samples])
    
    def generate_hybrid(
        self,
        original_data: pd.DataFrame,
        categorical_columns: List[str],
        num_samples: int,
        ctgan_model=None,
        config: Optional[GenerationConfig] = None
    ) -> pd.DataFrame:
        """
        Generate synthetic data using hybrid CTGAN + Gemini approach.
        
        Args:
            original_data: Original dataset
            categorical_columns: List of categorical column names
            num_samples: Number of synthetic samples to generate
            ctgan_model: Pre-trained CTGAN model (optional)
            config: Generation configuration
            
        Returns:
            DataFrame with synthetic data
        """
        config = config or GenerationConfig()
        
        # Step 1: Analyze patterns in original data
        logger.info("Analyzing data patterns...")
        patterns = self.analyze_data_patterns(original_data, categorical_columns)
        
        # Step 2: Generate CTGAN samples for structure (if model provided)
        ctgan_samples = None
        if ctgan_model is not None:
            logger.info("Generating CTGAN base samples...")
            ctgan_samples = ctgan_model.sample(num_samples)
        
        # Step 3: Try Gemini enhancement
        if config.use_gemini and self.is_available:
            try:
                logger.info("Enhancing with Gemini API...")
                return self.generate_with_gemini(
                    patterns=patterns,
                    num_samples=num_samples,
                    ctgan_samples=ctgan_samples,
                    config=config
                )
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}")
                if config.fallback_to_ctgan and ctgan_samples is not None:
                    logger.info("Falling back to CTGAN-only generation")
                    return ctgan_samples
                raise
        
        # Step 4: Fallback to CTGAN-only
        if ctgan_samples is not None:
            logger.info("Using CTGAN-only generation (Gemini not available)")
            return ctgan_samples
        
        raise RuntimeError("No generation method available. Provide CTGAN model or Gemini API key.")


def generate_synthetic_data_enhanced(
    input_file: str,
    categorical_columns: List[str],
    num_samples: int = 1000,
    use_gemini: bool = True,
    epochs: int = 100,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    High-level function for enhanced synthetic data generation.
    
    Combines CTGAN for statistical structure with Gemini for realistic values.
    """
    from ctgan import CTGAN
    
    # Load data
    df = pd.read_csv(input_file)
    processed_df = df[categorical_columns].copy()
    
    for col in categorical_columns:
        processed_df[col] = processed_df[col].fillna('MISSING').astype(str)
    
    # Train CTGAN
    logger.info("Training CTGAN model...")
    ctgan = CTGAN(
        epochs=epochs,
        batch_size=500,
        generator_dim=(128, 128),
        discriminator_dim=(128, 128),
        verbose=True
    )
    ctgan.fit(processed_df, discrete_columns=categorical_columns)
    
    # Generate with hybrid approach
    generator = GeminiSyntheticGenerator(api_key=api_key)
    config = GenerationConfig(use_gemini=use_gemini)
    
    synthetic_data = generator.generate_hybrid(
        original_data=processed_df,
        categorical_columns=categorical_columns,
        num_samples=num_samples,
        ctgan_model=ctgan,
        config=config
    )
    
    # Post-process
    for col in categorical_columns:
        synthetic_data[col] = synthetic_data[col].replace('MISSING', np.nan)
    
    return synthetic_data
