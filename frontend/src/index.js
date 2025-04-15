import React from "react";
import ReactDOM from "react-dom";
import "./output.css";
import UploadForm from "./UploadForm";
import { ApiProvider } from "./ApiContext";

ReactDOM.render(
  <div className="dark">
    <ApiProvider>
      <UploadForm />
    </ApiProvider>
  </div>,
  document.getElementById("root")
);
