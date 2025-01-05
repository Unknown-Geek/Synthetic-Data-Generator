import React, { createContext, useState, useEffect } from 'react';

export const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [apiUrl, setApiUrl] = useState(process.env.REACT_APP_API_URL);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkServer = async (url) => {
      try {
        const response = await fetch(`${url}/health`, { timeout: 5000 });
        return response.ok;
      } catch (error) {
        console.error(`Error connecting to server at ${url}:`, error);
        return false;
      }
    };

    const initializeApi = async () => {
      const developmentUrl = 'http://localhost:8080';
      const productionUrl = 'https://synthetic-data-generator-backend.onrender.com';

      // Try development server first
      if (await checkServer(developmentUrl)) {
        setApiUrl(developmentUrl);
        console.log('Using development server');
      }
      // Fall back to production server if development fails
      else if (await checkServer(productionUrl)) {
        setApiUrl(productionUrl);
        console.log('Using production server');
      }
      // If both fail, keep the default from env
      else {
        console.warn('Both development and production servers are unavailable, using default URL');
      }
      
      setIsLoading(false);
    };

    initializeApi();
  }, []);

  return (
    <ApiContext.Provider value={{ apiUrl, isLoading }}>
      {children}
    </ApiContext.Provider>
  );
};
