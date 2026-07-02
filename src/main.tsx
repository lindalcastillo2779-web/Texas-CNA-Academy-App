import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Missing #root element in index.html');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

const app = document.querySelector('#app') || document.body;

app.innerHTML = `
  <section style="padding:24px">
    <h2>Texas CNA Academy frontend connected ✅</h2>
    <p>Vite + TypeScript build is working.</p>
  </section>
`;
