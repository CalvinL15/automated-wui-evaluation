import './index.css';

import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import { SnackbarProvider } from 'notistack';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import App from './App';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center'
          }}
          autoHideDuration={5000}
        >
          <App />
        </SnackbarProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
