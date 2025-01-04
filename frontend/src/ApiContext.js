import React, { createContext, useState, useEffect } from 'react';

export const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [apiUrl, setApiUrl] = useState('https://synthetic-data-generator-backend.onrender.com');
  const [isLoading, setIsLoading] = useState(true);

  const checkServerHealth = async (url) => {
    try {
      const response = await fetch(`${url}/health`);
      return response.ok;
    } catch (error) {
      console.warn(`Could not connect to ${url}:`, error.message);
      return false;
    }
  };

  useEffect(() => {
    const initializeApi = async () => {
      const localUrl = 'http://localhost:8080';
      const prodUrl = 'https://synthetic-data-generator-backend.onrender.com';

      const isLocalHealthy = await checkServerHealth(localUrl);
      if (isLocalHealthy) {
        setApiUrl(localUrl);
      } else {
        const isProdHealthy = await checkServerHealth(prodUrl);
        if (isProdHealthy) {
          setApiUrl(prodUrl);
        }
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
