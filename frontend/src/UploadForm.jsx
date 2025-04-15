import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import GlassmorphismButton from "./components/GlassmorphismButton";
import { ApiContext } from "./ApiContext";

const UploadForm = () => {
  const {
    apiUrl,
    serverStatus: contextServerStatus,
    usingFallback,
    setProcessing
  } = useContext(ApiContext);
  const [file, setFile] = useState(null);
  const [categoricalColumns, setCategoricalColumns] = useState("");
  const [numSamples, setNumSamples] = useState(1000);
  const [downloadLink, setDownloadLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [validationError, setValidationError] = useState("");
  const [availableColumns, setAvailableColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [serverStatus, setServerStatus] = useState("checking");

  useEffect(() => {
    // Use the server status from context
    setServerStatus(contextServerStatus);

    // Only show error if server is offline AND we're not currently loading/processing
    if (contextServerStatus !== "online" && !loading) {
      setError("Server is not available");
    } else {
      // Remove error message when server is online or when loading
      setError("");
    }
  }, [contextServerStatus, usingFallback, loading]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFile(file);

    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const csvContent = event.target.result;
        const firstLine = csvContent.split("\n")[0];
        const headers = firstLine.split(",").map((header) => header.trim());
        setAvailableColumns(headers);
        setSelectedColumns([]);
        setCategoricalColumns("");
      };
      reader.readAsText(file);
    }
  };

  const handleColumnSelect = (column) => {
    setSelectedColumns((prev) => {
      const newSelection = prev.includes(column)
        ? prev.filter((col) => col !== column)
        : [...prev, column];
      setCategoricalColumns(newSelection.join(","));
      return newSelection;
    });
  };

  const validateForm = () => {
    if (!file) {
      setError("Please select a CSV file");
      return false;
    }

    if (!categoricalColumns.trim()) {
      setError("Please specify at least one categorical column");
      return false;
    }

    if (numSamples < 1) {
      setError("Number of samples must be greater than 0");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (serverStatus !== "online") {
      setError("Server is not available");
      return;
    }
    setLoading(true);
    setError("");
    setValidationError("");
    setDownloadLink("");
    setUploadProgress(0);
    
    // Tell context we're processing - prevents status changes
    setProcessing(true);

    if (!validateForm()) {
      setLoading(false);
      setProcessing(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("categorical_columns", categoricalColumns.trim());
    formData.append("num_samples", numSamples);

    try {
      const response = await axios.post(`${apiUrl}/generate`, formData, {
        responseType: "blob",
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      const contentType = response.headers["content-type"];
      if (contentType && contentType.includes("application/json")) {
        const reader = new FileReader();
        reader.onload = () => {
          const errorData = JSON.parse(reader.result);
          setError(errorData.error || "Unknown error occurred");
        };
        reader.readAsText(response.data);
      } else {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        setDownloadLink(url);
      }
    } catch (error) {
      console.error("Error:", error);
      if (error.response?.data instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorData = JSON.parse(reader.result);
            setError(errorData.error || "Error generating synthetic data");
          } catch (e) {
            setError("Error generating synthetic data");
          }
        };
        reader.readAsText(error.response.data);
      } else {
        setError(
          error.response?.data?.error || "Error generating synthetic data"
        );
      }
    } finally {
      setLoading(false);
      setUploadProgress(0);
      // Tell context we're done processing
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#0D0B1A] relative">
      <div className="absolute top-4 right-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-container px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 bg-gray-800/30 backdrop-blur-sm border border-gray-700/50"
        >
          <div
            className={`w-2 h-2 rounded-full ${
              serverStatus === "online"
                ? "bg-green-500" // Always green for online, even during fallback
                : serverStatus === "offline"
                ? "bg-red-500"
                : "bg-yellow-500 animate-pulse"
            }`}
          />
          <span className="text-sm text-white font-medium">
            Server:{" "}
            {serverStatus.charAt(0).toUpperCase() + serverStatus.slice(1)}
          </span>
        </motion.div>
      </div>
      <motion.form
        onSubmit={handleSubmit}
        className="glass-container w-full max-w-4xl p-8"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="text-4xl font-bold mb-8 text-white text-center gradient-text"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          Generate Synthetic Data
        </motion.h1>

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            className="md:col-span-2"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <label className="block text-white mb-2 font-semibold text-2xl">
              Upload CSV File
            </label>
            <div className="relative flex items-center justify-center w-full">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".csv"
                className="opacity-0 absolute inset-0 w-full h-full cursor-pointer z-10"
              />
              <div className="w-full bg-gray-800/50 border-2 border-dashed border-gray-600 rounded-lg p-6 text-center cursor-pointer transition-all duration-300 hover:border-violet-500 hover:bg-gray-700/50">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-12 w-12 mx-auto text-violet-500 mb-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <span className="text-gray-300">
                  {file ? (
                    <span>Selected: {file.name}</span>
                  ) : (
                    <span>
                      <span className="font-semibold">Click to upload</span> or
                      drag and drop
                      <br />
                      <span className="text-sm text-gray-400">
                        CSV files only
                      </span>
                    </span>
                  )}
                </span>
              </div>
            </div>
          </motion.div>

          {availableColumns.length > 0 && (
            <motion.div
              className="md:col-span-2"
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <label className="block text-white mb-2 font-semibold text-2xl">
                Select Categorical Columns
              </label>
              <div className="glass-container custom-scrollbar flex flex-wrap gap-3 max-h-48 overflow-y-auto p-4">
                {availableColumns.map((column) => (
                  <motion.div
                    key={column}
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
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
                        selectedColumns.includes(column)
                          ? "bg-violet-600 glow-effect"
                          : "bg-gray-700 hover:bg-violet-500"
                      }`}
                    >
                      {column}
                    </label>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          <motion.div
            className="md:col-span-2"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <label className="block text-white mb-2 font-semibold text-2xl">
              Number of Samples
            </label>
            <input
              type="number"
              value={numSamples}
              onChange={(e) => setNumSamples(parseInt(e.target.value))}
              min="1"
              className="w-full bg-gray-800/50 text-white border border-gray-700/50 rounded-lg p-3 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/50 transition-all duration-300"
            />
          </motion.div>
        </div>

        {uploadProgress > 0 && uploadProgress < 100 && (
          <motion.div
            className="mt-6"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="w-full bg-gray-700/30 rounded-full h-2">
              <div
                className="bg-violet-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm text-center mt-2 text-white">
              Uploading: {uploadProgress}%
            </p>
          </motion.div>
        )}

        {error && (
          <motion.div
            className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {error}
          </motion.div>
        )}

        {validationError && (
          <div className="text-red-500 text-sm mt-2">{validationError}</div>
        )}

        <GlassmorphismButton
          type="submit"
          disabled={loading}
          className="mt-8 w-full"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generating Data...
            </span>
          ) : (
            "Generate"
          )}
        </GlassmorphismButton>

        {downloadLink && (
          <motion.div
            className="mt-6 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <a
              href={downloadLink}
              download="synthetic_data.csv"
              className="inline-flex items-center px-6 py-3 bg-green-600/90 hover:bg-green-500/90 
                         text-white rounded-xl transition-all duration-300 transform hover:scale-[1.02]
                         backdrop-blur-sm"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download Synthetic Data
            </a>
          </motion.div>
        )}
      </motion.form>
    </div>
  );
};

export default UploadForm;
