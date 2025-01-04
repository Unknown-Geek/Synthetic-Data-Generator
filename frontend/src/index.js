import React from 'react';
import ReactDOM from 'react-dom';
import './output.css';
import UploadForm from './UploadForm';

// First try local server, then fall back to environment variable
export const API_URL = (() => {
  const localUrl = 'http://localhost:5000';
  
  // Function to check if local server is available
  const checkLocalServer = async () => {
    try {
      const response = await fetch(`${localUrl}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  // If local server is available, use it, otherwise use environment variable
  return checkLocalServer() ? localUrl : (process.env.REACT_APP_API_URL || localUrl);
})();

ReactDOM.render(
  <div className="dark">
    <UploadForm />
  </div>,
  document.getElementById('root')
);