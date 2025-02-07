import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  Input,
  Select,
  VStack,
} from '@chakra-ui/react';
import { analyzeBusiness } from '../services/businessApi';
import AnalysisResults from './AnalysisResults';
import type { AnalysisResponse } from '../services/businessApi';

export interface BusinessFormData {
  businessName: string;
  businessType: string;
  location: string;
  analysis_type: string;
}

const businessTypes = [
  'restaurant',
  'retail',
  'hotel',
  'service',
  'cafe',
  'salon',
  'fitness',
  'e-commerce'
];

const analysisTypes = [
  { value: 'dynamic_pricing', label: 'Dynamic Pricing' },
  { value: 'sentiment', label: 'Sentiment Analysis' },
  { value: 'competition', label: 'Competition Analysis' },
  { value: 'market', label: 'Market Analysis' },
  { value: 'pricing', label: 'Basic Pricing' }
];

const BusinessForm: React.FC = () => {
  const [formData, setFormData] = useState<BusinessFormData>({
    businessName: '',
    businessType: '',
    location: '',
    analysis_type: 'dynamic_pricing'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await analyzeBusiness(formData);
      setAnalysisData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Box as="form" onSubmit={handleSubmit} width="100%">
      <VStack spacing={4} align="stretch">
        <FormControl isRequired>
          <FormLabel>Business Name</FormLabel>
          <Input
            name="businessName"
            value={formData.businessName}
            onChange={handleInputChange}
            placeholder="Enter business name"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel>Business Type</FormLabel>
          <Select
            name="businessType"
            value={formData.businessType}
            onChange={handleInputChange}
            placeholder="Select business type"
          >
            {businessTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </Select>
        </FormControl>

        <FormControl isRequired>
          <FormLabel>Location</FormLabel>
          <Input
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            placeholder="Enter business location"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel>Analysis Type</FormLabel>
          <Select
            name="analysis_type"
            value={formData.analysis_type}
            onChange={handleInputChange}
          >
            {analysisTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={loading}
          loadingText="Analyzing..."
        >
          Analyze Business
        </Button>

        {error && (
          <Box color="red.500" mt={2}>
            {error}
          </Box>
        )}

        {analysisData && (
          <AnalysisResults 
            data={analysisData} 
            analysisType={formData.analysis_type}
          />
        )}
      </VStack>
    </Box>
  );
};

export default BusinessForm;
