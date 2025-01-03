from ctgan import CTGANSynthesizer
from sklearn.model_selection import train_test_split
import pandas as pd

def generate_synthetic_data(input_csv, output_csv, categorical_columns, sample_size=1000):
    # Load real dataset
    data = pd.read_csv(input_csv)

    # Split into training data
    train_data, _ = train_test_split(data, test_size=0.2)

    # Train the CTGAN model
    synthesizer = CTGANSynthesizer()
    synthesizer.fit(train_data, discrete_columns=categorical_columns)

    # Generate synthetic data
    synthetic_data = synthesizer.sample(sample_size)
    synthetic_data.to_csv(output_csv, index=False)

    print("Synthetic dataset saved successfully!")
