import React from 'react';
import ReactDOM from 'react-dom';
import './output.css';
import UploadForm from './UploadForm';
import { ApiProvider } from './ApiContext';

ReactDOM.render(
  <ApiProvider>
    <div className="dark">
      <UploadForm />
    </div>
  </ApiProvider>,
  document.getElementById('root')
);