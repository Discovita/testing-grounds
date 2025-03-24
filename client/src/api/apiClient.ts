/**
 * apiClient.ts
 * 
 * This file creates and configures the axios instance used for all API requests.
 * It provides the base URL and default configuration for API requests.
 */

import axios from 'axios';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Base URL for the State Machine Demo API
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient; 