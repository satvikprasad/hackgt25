import '../globals.css';

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

import { io } from 'socket.io-client';

const socket = io('http://127.0.0.1:5000')

socket.on()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
