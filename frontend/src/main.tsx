import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { Provider } from 'react-redux'
import { store } from "@/store/store";
import { ThemeProvider } from './components/theme-provider';
import { Analytics } from "@vercel/analytics/react"


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <Provider store={store}>
        <App />
        <Analytics />
      </Provider>
    </ThemeProvider>
  </StrictMode>,
)
