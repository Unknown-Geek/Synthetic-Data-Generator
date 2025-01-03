import React from 'react';
import ReactDOM from 'react-dom';
import './site.css';

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <h1 className="text-4xl font-bold text-blue-500">Hello, Tailwind CSS!</h1>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));