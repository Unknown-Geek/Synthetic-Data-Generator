import axios from "axios";

/**
 * Check health of a server
 * @param {string} url - API URL to check
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<Object>} - Status result object
 */
const checkSingleServerHealth = async (url, timeout = 5000) => {
  try {
    const response = await axios.get(`${url}/health`, { timeout });

    if (response.data.status === "healthy") {
      return {
        status: "online",
        error: null,
        details: response.data,
        url,
      };
    } else {
      return {
        status: "offline",
        error: "Server is not responding properly",
        details: response.data,
        url,
      };
    }
  } catch (err) {
    console.error(`Server connection error for ${url}:`, err);

    // Determine more specific error message
    let errorMessage = "Cannot connect to server";
    if (err.code === "ECONNABORTED") {
      errorMessage = "Connection timed out";
    } else if (err.response) {
      errorMessage = `Server error: ${err.response.status}`;
    } else if (err.request) {
      errorMessage = "No response from server";
    }

    return {
      status: "offline",
      error: errorMessage,
      details: { error: err.message },
      url,
    };
  }
};

/**
 * Check server health with fallback mechanism
 * Tries the primary server first, falls back to production if not available
 */
const checkServerHealth = async (primaryUrl, productionUrl = null) => {
  // If production URL is not provided, use only primary URL
  if (!productionUrl) {
    return await checkSingleServerHealth(primaryUrl);
  }

  // Try primary server first
  const primaryStatus = await checkSingleServerHealth(primaryUrl);

  // If primary is online, return it
  if (primaryStatus.status === "online") {
    return primaryStatus;
  }

  // If primary is offline, try production
  console.log("Primary server offline, trying production server...");
  const productionStatus = await checkSingleServerHealth(productionUrl);

  // If production is online, use it but mark as fallback
  if (productionStatus.status === "online") {
    return {
      ...productionStatus,
      isFallback: true,
      primaryError: primaryStatus.error,
    };
  }

  // If both are offline, return primary status
  return primaryStatus;
};

export { checkServerHealth, checkSingleServerHealth };
