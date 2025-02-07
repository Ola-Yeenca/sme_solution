import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  useToast,
  Container,
  Heading,
  Select,
  Flex,
  useColorModeValue,
  HStack,
  Switch,
  ScaleFade,
  FormErrorMessage,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { FiRefreshCw } from 'react-icons/fi';

const MotionBox = motion(Box);

interface DynamicPricingFormProps {
  onSubmit: (data: any) => Promise<void>;
  isLoading: boolean;
}

const BUSINESS_TYPES = [
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'retail', label: 'Retail Store' },
  { value: 'service', label: 'Service Business' },
  { value: 'cafe', label: 'Café' },
  { value: 'salon', label: 'Salon/Spa' },
  { value: 'fitness', label: 'Fitness Center' },
  { value: 'other', label: 'Other' },
];

export const DynamicPricingForm: React.FC<DynamicPricingFormProps> = ({
  onSubmit,
  isLoading
}) => {
  const toast = useToast();
  const [businessName, setBusinessName] = useState('');
  const [businessType, setBusinessType] = useState('');
  const [language, setLanguage] = useState('EN');
  const [errors, setErrors] = useState<{
    business_name?: string;
    business_type?: string;
  }>({});

  const validateForm = () => {
    const newErrors: {
      business_name?: string;
      business_type?: string;
    } = {};

    if (!businessName.trim()) {
      newErrors.business_name = 'Business name is required';
    }

    if (!businessType) {
      newErrors.business_type = 'Business type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      try {
        await onSubmit({
          business_name: businessName.trim(),
          business_type: businessType,
          analysis_type: 'dynamic_pricing'
        });
      } catch (error: any) {
        toast({
          title: 'Error',
          description: error.message || 'Failed to analyze',
          status: 'error',
          duration: 5000,
          isClosable: true
        });
      }
    }
  };

  const bgColor = useColorModeValue('gray.900', 'gray.800');
  const cardBg = useColorModeValue('gray.800', 'gray.700');
  const inputBg = useColorModeValue('gray.700', 'gray.600');
  const borderColor = useColorModeValue('gray.700', 'gray.600');

  return (
    <Box bg={bgColor} color="white">
      {/* Header */}
      <Box py={4} px={6}>
        <Flex justify="space-between" align="center">
          <Text fontSize="xl" fontWeight="bold">
            <Box as="span" color="blue.400">Valencia</Box> SME
          </Text>
          <HStack spacing={4}>
            <Button
              size="sm"
              variant="ghost"
              color={language === 'EN' ? 'blue.400' : 'gray.400'}
              onClick={() => setLanguage('EN')}
            >
              EN
            </Button>
            <Button
              size="sm"
              variant="ghost"
              color={language === 'ES' ? 'blue.400' : 'gray.400'}
              onClick={() => setLanguage('ES')}
            >
              ES
            </Button>
            <Switch colorScheme="blue" size="sm" />
          </HStack>
        </Flex>
      </Box>

      <Container maxW="container.sm" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Analysis Form */}
          <ScaleFade in={true} initialScale={0.9}>
            <Box
              as="form"
              onSubmit={handleSubmit}
              bg={cardBg}
              borderRadius="2xl"
              p={6}
              border="1px solid"
              borderColor={borderColor}
            >
              <VStack spacing={6}>
                <FormControl isRequired isInvalid={!!errors.business_name}>
                  <FormLabel color="gray.400">Business Name</FormLabel>
                  <Input
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    placeholder="Enter your business name"
                    bg={inputBg}
                    border="1px solid"
                    borderColor={borderColor}
                    _hover={{
                      borderColor: 'blue.500',
                    }}
                    _focus={{
                      borderColor: 'blue.500',
                      boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                    }}
                  />
                  <FormErrorMessage>{errors.business_name}</FormErrorMessage>
                </FormControl>

                <FormControl isRequired isInvalid={!!errors.business_type}>
                  <FormLabel color="gray.400">Business Type</FormLabel>
                  <Select
                    value={businessType}
                    onChange={(e) => setBusinessType(e.target.value)}
                    placeholder="Select business type"
                    bg={inputBg}
                    border="1px solid"
                    borderColor={borderColor}
                    _hover={{
                      borderColor: 'blue.500',
                    }}
                    _focus={{
                      borderColor: 'blue.500',
                      boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                    }}
                  >
                    {BUSINESS_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Select>
                  <FormErrorMessage>{errors.business_type}</FormErrorMessage>
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  width="full"
                  isLoading={isLoading}
                  loadingText="Analyzing..."
                  leftIcon={<FiRefreshCw />}
                >
                  Analyze Pricing
                </Button>
              </VStack>
            </Box>
          </ScaleFade>
        </VStack>
      </Container>
    </Box>
  );
};