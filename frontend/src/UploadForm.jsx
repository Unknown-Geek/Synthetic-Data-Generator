import React, { useState, useContext } from 'react';
import axios from 'axios';
import { ApiContext } from './ApiContext';

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [categoricalColumns, setCategoricalColumns] = useState('');
  const [numSamples, setNumSamples] = useState(1000);
  const [downloadLink, setDownloadLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [validationError, setValidationError] = useState('');
  const [availableColumns, setAvailableColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);

  const { apiUrl, isLoading } = useContext(ApiContext);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFile(file);
    
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const csvContent = event.target.result;
        const firstLine = csvContent.split('\n')[0];
        const headers = firstLine.split(',').map(header => header.trim());
        setAvailableColumns(headers);
        setSelectedColumns([]); // Reset selections when new file is uploaded
        setCategoricalColumns(''); // Reset text input
      };
      reader.readAsText(file);
    }
  };

  const handleColumnSelect = (column) => {
    setSelectedColumns(prev => {
      const newSelection = prev.includes(column)
        ? prev.filter(col => col !== column)
        : [...prev, column];
      setCategoricalColumns(newSelection.join(','));
      return newSelection;
    });
  };

  const validateForm = () => {
    if (!file) {
      setError('Please select a CSV file');
      return false;
    }
    
    if (!categoricalColumns.trim()) {
      setError('Please specify at least one categorical column');
      return false;
    }

    if (numSamples < 1) {
      setError('Number of samples must be greater than 0');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setValidationError('');
    setDownloadLink('');
    setUploadProgress(0);

    if (isLoading) {
      setError('Waiting for server connection...');
      return;
    }

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('categorical_columns', categoricalColumns.trim());
    formData.append('num_samples', numSamples);

    try {
      const response = await axios.post(`${apiUrl}/generate`, formData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      // Check if the response is an error message
      const contentType = response.headers['content-type'];
      if (contentType && contentType.includes('application/json')) {
        // Parse error message
        const reader = new FileReader();
        reader.onload = () => {
          const errorData = JSON.parse(reader.result);
          setError(errorData.error || 'Unknown error occurred');
        };
        reader.readAsText(response.data);
      } else {
        // Handle successful response
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadLink(url);
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.response?.data instanceof Blob) {
        // Try to read error message from blob
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorData = JSON.parse(reader.result);
            setError(errorData.error || 'Error generating synthetic data');
          } catch (e) {
            setError('Error generating synthetic data');
          }
        };
        reader.readAsText(error.response.data);
      } else {
        setError(error.response?.data?.error || 'Error generating synthetic data');
      }
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      <form onSubmit={handleSubmit} className="glass-container rounded-2xl shadow-2xl w-full max-w-4xl p-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-8 text-white text-center animate-slide-in">
          Generate Synthetic Data
        </h1>
        
        <div className="grid md:grid-cols-2 gap-6">
        {/* File Upload Section */}
        <div className="md:col-span-2 animate-slide-in" style={{ animationDelay: '0.1s' }}>
            <label className="block text-white mb-2 font-semibold" style={{ fontSize: '23px' }}>Upload CSV File</label>
            <div className="file-input-wrapper">
                <input 
                    type="file" 
                    onChange={handleFileChange}
                    accept=".csv"
                    className="file-input"
                />
                <div className="file-input-button">
                    <div className="icon">
                        {file ? (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                        )}
                    </div>
                    <div className="text">
                        {file ? (
                            <span>Selected: {file.name}</span>
                        ) : (
                            <span>
                                <span className="font-semibold">Click to upload</span> or drag and drop<br />
                                <span className="text-sm text-gray-400">CSV files only</span>
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>

        {/* Column Selection Section */}
          {availableColumns.length > 0 && (
            <div className="md:col-span-2 animate-slide-in" style={{ animationDelay: '0.2s' }}>
              <label className="block text-white mb-2 font-semibold" style={{ fontSize: '23px' }}>Select Categorical Columns</label>
              <div className="checkbox-container custom-scrollbar flex flex-wrap gap-3 max-h-48 overflow-y-auto">
                {availableColumns.map(column => (
                  <div key={column} className="flex items-center space-x-2 p-2 hover:bg-gray-700/30 rounded-lg transition-colors">
                    <input
                      type="checkbox"
                      id={column}
                      checked={selectedColumns.includes(column)}
                      onChange={() => handleColumnSelect(column)}
                      className="hidden"
                    />
                    <label 
                      htmlFor={column} 
                      className={`cursor-pointer text-sm text-white py-2 px-4 rounded-lg transition-all duration-300 ${
                        selectedColumns.includes(column) ? 'bg-violet-600' : 'bg-gray-700'
                      } hover:bg-violet-500`}
                    >
                      {column}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Number of Samples */}
          <div className="md:col-span-2 animate-slide-in" style={{ animationDelay: '0.3s' }}>
            <label className="block text-white mb-2 font-semibold" style={{ fontSize: '23px' }}>Number of Samples</label>
            <input
              type="number"
              value={numSamples}
              onChange={(e) => setNumSamples(e.target.value)}
              min="1"
              className="w-full"
            />
          </div>
        </div>

        {/* Progress Bar */}
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="mt-6 animate-fade-in">
            <div className="w-full bg-gray-700/30 rounded-full h-2">
              <div 
                className="bg-violet-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm text-center mt-2 text-white">Uploading: {uploadProgress}%</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-center animate-fade-in">
            {error}
          </div>
        )}

        {/* Validation Error Message */}
        {validationError && (
          <div className="text-red-500 text-sm mt-2">
            {validationError}
          </div>
        )}

        {/* Submit Button */}
        <button 
          type="submit" 
          disabled={loading}
          className="mt-8 w-full bg-violet-600 hover:bg-violet-500 text-white py-4 px-6 rounded-xl
                   font-bold transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50
                   disabled:hover:scale-100 animate-slide-in shadow-lg"
          style={{ animationDelay: '0.4s' }}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Data...
            </span>
          ) : 'Generate'}
        </button>

        {/* Download Link */}
        {downloadLink && (
          <div className="mt-6 text-center animate-fade-in">
            <a 
              href={downloadLink} 
              download="synthetic_data.csv" 
              className="inline-flex items-center px-6 py-3 bg-green-600/90 hover:bg-green-500/90 
                       text-white rounded-xl transition-all duration-300 transform hover:scale-[1.02]
                       backdrop-blur-sm animate-pulse-slow"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download Synthetic Data
            </a>
          </div>
        )}
      </form>
    </div>
  );
};

export default UploadForm;