/**
 * API Configuration
 * 
 * Centralized API configuration for the frontend.
 */

// Base API path - uses Next.js proxy via rewrites
const API_BASE_PATH = '/api/py';

// API version
const API_VERSION = 'v1';

// Construct versioned base path
export const API_BASE_URL = `${API_BASE_PATH}/${API_VERSION}`;

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // ETF endpoints
  ETF: {
    CREATE_ANALYSIS: `${API_BASE_URL}/etfs`,  // POST - Create new ETF analysis
    HEALTH: `${API_BASE_URL}/health`,          // GET - Health check
  },
  
  // Root API info
  ROOT: API_BASE_PATH,  // GET - API information
} as const;

/**
 * Helper function to build API URLs
 * Can be extended to handle query parameters, path parameters, etc.
 */
export function buildApiUrl(endpoint: string, params?: Record<string, string>): string {
  let url = endpoint;
  
  if (params) {
    const queryString = new URLSearchParams(params).toString();
    url = `${url}?${queryString}`;
  }
  
  return url;
}

/**
 * API Error Messages
 * Centralized error messages for consistency
 */
export const API_ERRORS = {
  UPLOAD_FAILED: 'Failed to upload file. Please try again.',
  INVALID_FILE: 'Please select a valid CSV file.',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
} as const;

