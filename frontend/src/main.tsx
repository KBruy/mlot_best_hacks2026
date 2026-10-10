import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { PxlKitSurfaceProvider, PxlKitToastProvider } from '@pxlkit/ui-kit'
import './styles/base.css'
import App from './App.tsx'

document.documentElement.classList.add('dark')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PxlKitSurfaceProvider surface="pixel">
      <PxlKitToastProvider>
        <App />
      </PxlKitToastProvider>
    </PxlKitSurfaceProvider>
  </StrictMode>,
)
