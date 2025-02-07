import React from 'react';
import {
  Box,
  Card,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  VStack,
  Text,
  Badge,
  List,
  ListItem,
  ListIcon,
  Flex,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Alert,
  AlertIcon,
  AlertDescription
} from '@chakra-ui/react';
import { 
  MdTrendingUp,
  MdTrendingDown,
  MdTrendingFlat,
  MdCheckCircle
} from 'react-icons/md';

interface Competitor {
  name: string;
  rating: number;
  review_count: number;
  price_level: string;
  source: string;
}

interface PriceDistribution {
  segments: {
    budget: number;
    economy: number;
    mid_range: number;
    premium: number;
    luxury: number;
  };
  percentiles: {
    p10: number;
    p25: number;
    p50: number;
    p75: number;
    p90: number;
  };
  distribution_metrics: {
    mean: number;
    median: number;
    std: number;
    skewness: number;
    kurtosis: number;
  };
}

interface RealTimeFactors {
  time_factors: {
    hour: number;
    day_of_week: number;
    is_weekend: boolean;
    is_business_hours: boolean;
    is_peak_hours: boolean;
  };
  demand_factors: {
    current_utilization: number;
    demand_level: string;
    recent_bookings: number;
    waiting_list: number;
  };
  special_conditions: {
    has_event: boolean;
    has_promotion: boolean;
    has_holiday: boolean;
    weather_impact: number;
  };
  timestamp: string;
}

interface MarketData {
  competitor_pricing?: {
    average: number;
    range: {
      min: number;
      max: number;
    };
  };
  customer_segments?: Array<{
    name: string;
    size: string;
    price_sensitivity: string;
  }>;
  demand_patterns?: Array<{
    pattern: string;
    impact: string;
  }>;
  position?: string;
}

interface Recommendation {
  optimal_price_range?: {
    min: number;
    max: number;
    recommended: number;
  };
  price_positioning?: string;
  seasonal_adjustments?: Array<{
    season: string;
    adjustment: string;
  }>;
  special_offers?: Array<{
    name: string;
    description: string;
    discount: string;
  }>;
}

interface Metrics {
  confidence: number;
  data_freshness: number;
  market_coverage: number;
}

interface DynamicPricingResultsProps {
  status: string;
  market_data?: MarketData;
  recommendation?: Recommendation;
  metrics?: Metrics;
}

export const DynamicPricingResults: React.FC<DynamicPricingResultsProps> = ({ status, market_data, recommendation, metrics }) => {
  if (status === 'error') {
    return (
      <Alert status="error" variant="subtle">
        <AlertIcon />
        <AlertDescription>
          No analysis data available. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  if (!market_data || !recommendation) {
    return (
      <Alert status="warning" variant="subtle">
        <AlertIcon />
        <AlertDescription>
          No pricing analysis data available.
        </AlertDescription>
      </Alert>
    );
  }

  const getTrendIcon = (value: number) => {
    if (value > 0) return MdTrendingUp;
    if (value < 0) return MdTrendingDown;
    return MdTrendingFlat;
  };

  return (
    <VStack spacing={6} align="stretch" w="full">
      {/* Market Data Section */}
      {market_data && (
        <Card p={6} bg="gray.800" color="white">
          <VStack spacing={4} align="stretch">
            <Text fontSize="xl" fontWeight="bold">
              Market Analysis
            </Text>
            
            {market_data.competitor_pricing && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Competitor Pricing</h4>
                <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Average Price</StatLabel>
                      <StatNumber>${market_data.competitor_pricing.average.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Minimum Price</StatLabel>
                      <StatNumber>${market_data.competitor_pricing.range.min.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Maximum Price</StatLabel>
                      <StatNumber>${market_data.competitor_pricing.range.max.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                </Grid>
              </div>
            )}

            {market_data.position && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Market Position</h4>
                <Text fontSize="lg">{market_data.position}</Text>
              </div>
            )}

            {market_data.customer_segments && market_data.customer_segments.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Customer Segments</h4>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  {market_data.customer_segments.map((segment, index) => (
                    <GridItem key={index}>
                      <Box bg="whiteAlpha.100" p={4} borderRadius="lg">
                        <Text fontSize="lg" fontWeight="bold">{segment.name}</Text>
                        <Text fontSize="md" color="gray.600">
                          ({segment.size} | Sensitivity: {segment.price_sensitivity})
                        </Text>
                      </Box>
                    </GridItem>
                  ))}
                </Grid>
              </div>
            )}
          </VStack>
        </Card>
      )}

      {/* Recommendations Section */}
      {recommendation && (
        <Card p={6} bg="gray.800" color="white">
          <VStack spacing={4} align="stretch">
            <Text fontSize="xl" fontWeight="bold">
              Pricing Recommendations
            </Text>

            {recommendation.optimal_price_range && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Optimal Price Range</h4>
                <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Recommended Price</StatLabel>
                      <StatNumber>${recommendation.optimal_price_range.recommended.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Minimum Price</StatLabel>
                      <StatNumber>${recommendation.optimal_price_range.min.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                  <GridItem>
                    <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                      <StatLabel>Maximum Price</StatLabel>
                      <StatNumber>${recommendation.optimal_price_range.max.toFixed(2)}</StatNumber>
                    </Stat>
                  </GridItem>
                </Grid>
              </div>
            )}

            {recommendation.price_positioning && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Price Positioning</h4>
                <Text fontSize="lg">{recommendation.price_positioning}</Text>
              </div>
            )}

            {recommendation.seasonal_adjustments && recommendation.seasonal_adjustments.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">Seasonal Adjustments</h4>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  {recommendation.seasonal_adjustments.map((adjustment, index) => (
                    <GridItem key={index}>
                      <Box bg="whiteAlpha.100" p={4} borderRadius="lg">
                        <Text fontSize="lg" fontWeight="bold">{adjustment.season}</Text>
                        <Flex align="center">
                          <Icon
                            as={getTrendIcon(parseFloat(adjustment.adjustment))}
                            color={parseFloat(adjustment.adjustment) > 0 ? 'green.500' : 'red.500'}
                            mr={2}
                          />
                          {adjustment.adjustment}
                        </Flex>
                      </Box>
                    </GridItem>
                  ))}
                </Grid>
              </div>
            )}

            {recommendation.special_offers && recommendation.special_offers.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Special Offers</h4>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  {recommendation.special_offers.map((offer, index) => (
                    <GridItem key={index}>
                      <Box bg="whiteAlpha.100" p={4} borderRadius="lg">
                        <Text fontSize="lg" fontWeight="bold">{offer.name}</Text>
                        <Text fontSize="md" color="gray.600">{offer.description}</Text>
                        <Badge colorScheme="green">Discount: {offer.discount}</Badge>
                      </Box>
                    </GridItem>
                  ))}
                </Grid>
              </div>
            )}
          </VStack>
        </Card>
      )}

      {/* Metrics Section */}
      {metrics && (
        <Card p={6} bg="gray.800" color="white">
          <VStack spacing={4} align="stretch">
            <Text fontSize="xl" fontWeight="bold">
              Analysis Metrics
            </Text>
            <Grid templateColumns="repeat(3, 1fr)" gap={4}>
              <GridItem>
                <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                  <StatLabel>Confidence Score</StatLabel>
                  <Progress value={(metrics.confidence * 100).toFixed(0)} size="lg" borderRadius="lg" />
                  <StatNumber>{(metrics.confidence * 100).toFixed(0)}%</StatNumber>
                </Stat>
              </GridItem>
              <GridItem>
                <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                  <StatLabel>Data Freshness</StatLabel>
                  <Progress value={(metrics.data_freshness * 100).toFixed(0)} size="lg" borderRadius="lg" />
                  <StatNumber>{(metrics.data_freshness * 100).toFixed(0)}%</StatNumber>
                </Stat>
              </GridItem>
              <GridItem>
                <Stat bg="whiteAlpha.100" p={4} borderRadius="lg">
                  <StatLabel>Market Coverage</StatLabel>
                  <Progress value={(metrics.market_coverage * 100).toFixed(0)} size="lg" borderRadius="lg" />
                  <StatNumber>{(metrics.market_coverage * 100).toFixed(0)}%</StatNumber>
                </Stat>
              </GridItem>
            </Grid>
          </VStack>
        </Card>
      )}
    </VStack>
  );
};