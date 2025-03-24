/**
 * QueryProvider.tsx
 * 
 * This component provides the TanStack Query client to the entire application.
 * It initializes the QueryClient with default options and wraps the application
 * with the QueryClientProvider to make React Query available throughout the app.
 */

import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/**
 * QueryClientProvider props
 * @property {ReactNode} children - Child components that will have access to the query client
 */
interface QueryProviderProps {
  children: ReactNode;
}

/**
 * Default configuration for the QueryClient
 * These settings affect how queries and mutations behave throughout the app
 */
const defaultOptions = {
  queries: {
    refetchOnWindowFocus: false, // Don't refetch queries when window regains focus
    retry: 1, // Only retry failed queries once
    staleTime: 1000 * 60 * 5, // Data is considered fresh for 5 minutes
  },
};

// Create a new QueryClient instance with default options
const queryClient = new QueryClient({
  defaultOptions,
});

/**
 * QueryProvider component
 * Provides the QueryClient to all child components
 */
export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
} 