import { createBrowserRouter } from 'react-router-dom';
import App from '../App';
import { ErrorBoundary } from '../components/ErrorBoundary';

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    ),
  },
  // Add more routes as needed
]);
