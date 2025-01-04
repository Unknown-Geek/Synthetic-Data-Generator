import React from 'react';
import ReactDOM from 'react-dom';
import './output.css';
import UploadForm from './UploadForm';
import { ApiProvider } from './ApiContext';

// API URL configuration
const LOCAL_API_URL = 'http://localhost:8080';  // Update local port to match Railway
const PROD_API_URL = 'https://synthetic-data-generator-backend-production.up.railway.app';

// Health check function with timeout
const checkServerHealth = async (url, timeout = 5000) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    const response = await fetch(`${url}/health`, {
      signal: controller.signal,
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    });
    
    clearTimeout(timeoutId);
    const data = await response.json();
    console.log(`Health check response from ${url}:`, data);
    return response.ok;
  } catch (error) {
    console.warn(`Could not connect to ${url}:`, error.message);
    return false;
  }
};

// Initialize API_URL with proper fallback
let API_URL = LOCAL_API_URL;

// Check local server first, then fall back to production
checkServerHealth(LOCAL_API_URL).then(isLocalHealthy => {
  if (!isLocalHealthy && PROD_API_URL) {
    console.log('Local server not available, falling back to production server...');
    checkServerHealth(PROD_API_URL).then(isProdHealthy => {
      if (isProdHealthy) {
        API_URL = PROD_API_URL;
        console.log(`Using production server at ${API_URL}`);
      } else {
        console.error('Neither local nor production servers are available');
      }
    });
  } else {
    console.log(`Using local server at ${API_URL}`);
  }
});

ReactDOM.render(
  <ApiProvider>
    <div className="dark">
      <UploadForm />
    </div>
  </ApiProvider>,
  document.getElementById('root')
);

// Export for use in other components
export { API_URL };