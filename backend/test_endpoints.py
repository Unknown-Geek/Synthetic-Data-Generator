import requests
import pandas as pd
import os

def test_backend():
    # Get absolute path to test data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_path = os.path.join(os.path.dirname(current_dir), 'test_data.csv')
    
    # Test health check
    health_response = requests.get('http://localhost:5000/health')
    print(f"Health check status: {health_response.status_code}")
    print(f"Health check response: {health_response.json()}")

    # Test data generation
    with open(test_data_path, 'rb') as f:
        files = {'file': f}
        data = {
            'categorical_columns': 'name,city',
            'num_samples': 10  # Change from string to integer
        }
        
        try:
            response = requests.post('http://localhost:5000/generate', files=files, data=data)
            
            if response.status_code == 200:
                # Save the response content to a file in the output directory
                output_dir = os.path.join(current_dir, 'output')
                os.makedirs(output_dir, exist_ok=True)
                # output_file = os.path.join(output_dir, 'test_output.csv')
                
                # with open(output_file, 'wb') as f:
                #     f.write(response.content)
                
                # # Read and display the first few rows
                # df = pd.read_csv(output_file)
                # print("\nGenerated Data Preview:")
                # print(df.head())
                # print(f"\nShape of generated data: {df.shape}")
                
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_backend()
