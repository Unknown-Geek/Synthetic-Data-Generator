import React from 'react';
import ReactDOM from 'react-dom';
import './output.css';
import UploadForm from './UploadForm';
import { Analytics } from '@vercel/analytics/react';

ReactDOM.render(
  <div className="dark">
    <UploadForm />
    <Analytics />
  </div>,
  document.getElementById('root')
);
