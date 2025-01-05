import React, { createContext, useState, useEffect } from 'react';

export const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [apiUrl] = useState(process.env.REACT_APP_API_URL);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkServer = async () => {
      try {
        const response = await fetch(`${apiUrl}/health`);
        if (!response.ok) {
          console.warn('API server is not responding');
        }
      } catch (error) {
        console.error('Error connecting to API server:', error);
      }
      setIsLoading(false);
    };

    checkServer();
  }, [apiUrl]);

  return (
    <ApiContext.Provider value={{ apiUrl, isLoading }}>
      {children}
    </ApiContext.Provider>
  );
};
