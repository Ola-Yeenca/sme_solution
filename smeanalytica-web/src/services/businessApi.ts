import type { BusinessFormData } from '../components/BusinessForm';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const API_KEY = process.env.NEXT_PUBLIC_BACKEND_API_KEY;
const API_BASE_URL = API_URL;

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface BusinessFormData {
  businessName: string;
  businessType: string;
  location: string;
  analysis_type: string;
}

export interface Recommendation {
  pricing_strategy: 'increase' | 'decrease' | 'maintain';
  confidence: number;
  explanation: string;
  suggested_actions: string[];
}

export interface MarketData {
  competitors: Array<{
    name: string;
    rating: number;
    review_count: number;
    price_level: string;
    source: string;
  }>;
  average_competitor_rating: number;
  average_competitor_price_level: string;
  market_position: string;
}

export interface AnalysisData {
  market_data: MarketData;
  recommendation: Recommendation;
}

export interface AnalysisResponse extends ApiResponse<AnalysisData> {}

export const analyzeBusiness = async (formData: BusinessFormData): Promise<AnalysisResponse> => {
  try {
    console.log('Making API request to:', `${API_BASE_URL}/analysis/analyze`);
    const response = await axios.post(`${API_BASE_URL}/analysis/analyze`, {
      business_name: formData.businessName,
      business_type: formData.businessType,
      location: formData.location || 'Valencia, Spain',
      analysis_type: formData.analysis_type
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      }
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.error || 'Failed to analyze business';
      console.error('API Error:', errorMessage);
      throw new Error(errorMessage);
    }
    throw error;
  }
};

export async function getBusinessTypes(): Promise<string[]> {
  try {
    console.log('Fetching business types from:', `${API_BASE_URL}/data/business-types`);
    
    const response = await fetch(`${API_BASE_URL}/data/business-types`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'X-API-Key': API_KEY || '',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.business_types || [];
  } catch (error) {
    console.error('Error fetching business types:', error);
    return [];
  }
}
