import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Collapse,
  Spinner,
  Center
} from '@chakra-ui/react';
import { DynamicPricingForm } from '../components/DynamicPricingForm';
import { DynamicPricingResults } from '../components/DynamicPricingResults';
import { api } from '../utils/api';

interface PricingResponse {
  status: string;
  recommendation: {
    pricing_strategy: 'increase' | 'decrease' | 'maintain';
    confidence: number;
    explanation: string;
    suggested_actions: string[];
  };
  market_data: {
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
  };
  error?: string;
}

export const DynamicPricingPage: React.FC = () => {
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [pricingResults, setPricingResults] = useState<PricingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: any) => {
    setIsLoading(true);
    setError(null);
    setPricingResults(null);

    try {
      const response = await api.post('/analyze/dynamic_pricing', {
        business_name: data.business_name,
        business_type: data.business_type,
        analysis_type: 'dynamic_pricing'
      });
      
      console.log('API Response:', response.data);
      
      if (response.data.status === 'error') {
        throw new Error(response.data.error || 'Failed to analyze pricing');
      }
      
      setPricingResults(response.data);
      
      toast({
        title: 'Analysis Complete',
        description: 'Your business insights are ready.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get pricing recommendation';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box textAlign="center">
          <Heading size="2xl" mb={4} color="white">
            Dynamic Pricing Optimization
          </Heading>
          <Text fontSize="lg" color="gray.400">
            Get AI-powered price recommendations based on real-time market conditions
          </Text>
        </Box>

        {error && (
          <Alert status="error" mb={6}>
            <AlertIcon />
            <Box>
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Box>
          </Alert>
        )}

        <Box>
          <DynamicPricingForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
        </Box>

        {isLoading && (
          <Center py={8}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
          </Center>
        )}

        {!isLoading && pricingResults && pricingResults.status === 'success' && (
          <Box mt={8}>
            <DynamicPricingResults
              status={pricingResults.status}
              recommendation={pricingResults.recommendation}
              market_data={pricingResults.market_data}
            />
          </Box>
        )}
      </VStack>
    </Container>
  );
};