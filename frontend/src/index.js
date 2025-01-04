import React from 'react';
import ReactDOM from 'react-dom';
import './output.css';
import UploadForm from './UploadForm';

// Access the API URL from environment variables
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

ReactDOM.render(
  <div className="dark">
    <UploadForm />
  </div>,
  document.getElementById('root')
);