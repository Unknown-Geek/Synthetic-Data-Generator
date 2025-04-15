import React, { createContext, useState, useEffect } from "react";
import { checkServerHealth } from "./utils/serverStatus";

export const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
  const [primaryApiUrl] = useState(process.env.REACT_APP_API_URL);
  const [productionApiUrl] = useState(process.env.REACT_APP_PRODUCTION_API_URL);
  const [activeApiUrl, setActiveApiUrl] = useState(primaryApiUrl);
  const [isLoading, setIsLoading] = useState(true);
  const [serverStatus, setServerStatus] = useState("checking");
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    const checkServer = async () => {
      try {
        const status = await checkServerHealth(primaryApiUrl, productionApiUrl);

        // Set the active API URL based on which server is available
        if (status.status === "online") {
          setActiveApiUrl(status.url);
          setUsingFallback(status.isFallback || false);
          setServerStatus("online"); // Always show as "online" even if fallback

          if (status.isFallback) {
            // Only log fallback status to console, don't expose in UI
            console.info(`Using production server at: ${status.url}`);
          }
        } else {
          console.warn("All API servers are offline");
          setServerStatus("offline");
        }
      } catch (error) {
        console.error("Error connecting to API servers:", error);
        setServerStatus("offline");
      }
      setIsLoading(false);
    };

    checkServer();
    // Check server status periodically
    const interval = setInterval(checkServer, 30000);
    return () => clearInterval(interval);
  }, [primaryApiUrl, productionApiUrl]);

  return (
    <ApiContext.Provider
      value={{
        apiUrl: activeApiUrl,
        isLoading,
        serverStatus,
        usingFallback, // Still provide this, but don't use it for visible UI elements
        primaryApiUrl,
        productionApiUrl,
      }}
    >
      {children}
    </ApiContext.Provider>
  );
};
