import axios from 'axios';

// Default API key for development - in production, this should be set via environment variable
const DEFAULT_API_KEY = 'smeanalytica-dev-12345';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_BACKEND_API_KEY || DEFAULT_API_KEY,
  },
});

export interface BusinessMetrics {
  revenue_growth: number;
  customer_satisfaction: number;
  market_share: number;
  competitor_analysis: {
    strengths: string[];
    opportunities: string[];
  };
  sentiment_analysis: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export const businessApi = {
  async getMetrics(businessName: string, businessType: string = 'restaurant'): Promise<BusinessMetrics> {
    try {
      const response = await api.post('/analysis/market', {
        business_name: businessName,
        business_type: businessType,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching business metrics:', error);
      throw error;
    }
  },

  async getAnalytics(businessName: string, businessType: string = 'restaurant') {
    try {
      const response = await api.post('/analysis/performance', {
        business_name: businessName,
        business_type: businessType,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  },

  async getSentimentAnalysis(businessName: string, businessType: string = 'restaurant') {
    try {
      const response = await api.post('/analysis/sentiment', {
        business_name: businessName,
        business_type: businessType,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching sentiment analysis:', error);
      throw error;
    }
  },
};
