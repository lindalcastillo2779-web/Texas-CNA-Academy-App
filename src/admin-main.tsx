import React from 'react';
import ReactDOM from 'react-dom/client';
import AdminApp from './admin/AdminApp';
import './styles/globals.css';

const rootElement = document.getElementById('app');

if (!rootElement) {
  throw new Error('Missing #app element in HTML entrypoint');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <AdminApp />
  </React.StrictMode>
);
