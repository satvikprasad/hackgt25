import '../globals.css';

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

//test

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
