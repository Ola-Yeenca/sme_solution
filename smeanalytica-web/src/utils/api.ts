import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for API key
api.interceptors.request.use(
  (config) => {
    const apiKey = localStorage.getItem('api_key');
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('api_key');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  pricing: {
    optimize: '/pricing/optimize',
    history: '/pricing/history',
    insights: '/pricing/insights'
  },
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    verify: '/auth/verify'
  }
};

// Helper functions for common API operations
export const apiHelpers = {
  setApiKey: (apiKey: string) => {
    localStorage.setItem('api_key', apiKey);
  },
  
  clearApiKey: () => {
    localStorage.removeItem('api_key');
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('api_key');
  }
};

// Error handling utilities
export const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error
    return {
      status: error.response.status,
      message: error.response.data.detail || 'An error occurred',
      data: error.response.data
    };
  } else if (error.request) {
    // Request made but no response
    return {
      status: 0,
      message: 'No response from server',
      data: null
    };
  } else {
    // Request setup error
    return {
      status: 0,
      message: error.message || 'Request failed',
      data: null
    };
  }
};

// Type definitions for API responses
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  data: any;
}

// Pricing types
export interface PricingRequest {
  business_name: string;
  business_type: string;
  preferences: {
    min_price?: number;
    max_price?: number;
    target_margin: number;
    max_price_change: number;
    maximize_revenue: boolean;
    stay_competitive: boolean;
    ensure_profit: boolean;
  };
}

export interface PricingResponse {
  current_optimal_price: number;
  price_range: {
    min: number;
    max: number;
  };
  real_time_factors: {
    demand_multiplier: number;
    competition_multiplier: number;
    time_multiplier: number;
    event_multiplier: number;
  };
  price_adjustments: Array<{
    reason: string;
    percentage: number;
    timing?: string;
  }>;
  timing: {
    next_update: string;
    peak_pricing_hours: string[];
  };
  insights: string[];
  confidence_score: number;
  currency: string;
  update_frequency: string;
  price_trends?: {
    trend: string;
    volatility: string;
  };
  historical_context?: {
    price_volatility: number;
    peak_prices: {
      highest: number;
      lowest: number;
      average: number;
    };
    optimal_times: string[];
  };
} 