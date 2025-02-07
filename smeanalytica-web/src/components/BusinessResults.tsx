import React from 'react';
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Icon,
  useColorModeValue,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { FaArrowUp, FaArrowDown, FaMinus, FaChartLine, FaUsers, FaStar, FaClock, FaChartBar, FaExclamationTriangle, FaSpinner } from 'react-icons/fa';
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  BarChart,
  LineChart,
  Line,
  CartesianGrid,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { motion } from 'framer-motion';
import { formatPrice } from '../utils/currency';

const MotionBox = motion(Box);
const MotionGridItem = motion(GridItem);

interface PriceTrends {
  historical_prices: Array<{
    timestamp: string;
    price: number;
  }>;
  seasonal_factors: Array<{
    factor: string;
    impact: number;
  }>;
  peak_hours: Array<{
    hour: number;
    demand: number;
  }>;
}

interface RealTimeFactors {
  demand_multiplier: number;
  competition_multiplier: number;
  time_multiplier: number;
  event_multiplier: number;
}

interface PriceRange {
  min: number;
  max: number;
}

interface Competitor {
  name: string;
  rating: number;
  review_count: number;
  price_level: string;
  source: string;
}

interface MarketData {
  competitors: Competitor[];
  average_competitor_rating: number;
  average_competitor_price_level: string;
  market_position: string;
  price_trends?: PriceTrends;
  real_time_factors?: RealTimeFactors;
  price_range?: PriceRange;
}

interface Recommendation {
  pricing_strategy: 'increase' | 'decrease' | 'maintain';
  confidence: number;
  explanation: string;
  suggested_actions: string[];
}

interface BusinessResultsProps {
  status: string;
  recommendation?: Recommendation;
  market_data?: MarketData;
  location: string;
}

const getPricingIcon = (strategy: string) => {
  switch (strategy) {
    case 'increase':
      return FaArrowUp;
    case 'decrease':
      return FaArrowDown;
    default:
      return FaMinus;
  }
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 80) return 'green';
  if (confidence >= 60) return 'yellow';
  return 'red';
};

export function BusinessResults({ status, recommendation, market_data, location }: BusinessResultsProps) {
  const cardBg = useColorModeValue('gray.800', 'gray.700');
  const textColor = useColorModeValue('gray.100', 'gray.200');
  const borderColor = useColorModeValue('gray.700', 'gray.600');

  if (status === 'error') {
    return (
      <Box
        p={6}
        bg={cardBg}
        borderRadius="xl"
        border="1px solid"
        borderColor={borderColor}
      >
        <VStack spacing={4} align="center">
          <Icon as={FaExclamationTriangle} w={12} h={12} color="red.400" />
          <Text color={textColor} fontSize="xl" textAlign="center">
            An error occurred while analyzing your business. Please try again.
          </Text>
        </VStack>
      </Box>
    );
  }

  if (status !== 'success' || !recommendation || !market_data) {
    return (
      <Box
        p={6}
        bg={cardBg}
        borderRadius="xl"
        border="1px solid"
        borderColor={borderColor}
      >
        <VStack spacing={4} align="center">
          <Icon as={FaSpinner} w={12} h={12} color="blue.400" />
          <Text color={textColor} fontSize="xl" textAlign="center">
            Analyzing your business...
          </Text>
        </VStack>
      </Box>
    );
  }

  // Prepare data for charts
  const competitorRatings = market_data.competitors.map(comp => ({
    name: comp.name,
    rating: comp.rating,
    reviews: comp.review_count,
  }));

  const priceDistribution = market_data.competitors.reduce((acc, comp) => {
    const priceLevel = comp.price_level.length;
    acc[priceLevel] = (acc[priceLevel] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);

  const priceData = Object.entries(priceDistribution).map(([level, count]) => ({
    priceLevel: '$'.repeat(Number(level)),
    count,
  }));

  // Real-time factors data for radar chart
  const realTimeFactors = market_data.real_time_factors
    ? [
        {
          factor: 'Demand',
          value: market_data.real_time_factors.demand_multiplier * 100,
        },
        {
          factor: 'Competition',
          value: market_data.real_time_factors.competition_multiplier * 100,
        },
        {
          factor: 'Time',
          value: market_data.real_time_factors.time_multiplier * 100,
        },
        {
          factor: 'Events',
          value: market_data.real_time_factors.event_multiplier * 100,
        },
      ]
    : [];

  // Peak hours data
  const peakHoursData = market_data.price_trends?.peak_hours.map(hour => ({
    hour: `${hour.hour}:00`,
    demand: hour.demand * 100,
  })) || [];

  return (
    <Grid
      templateColumns={{ base: 'repeat(1, 1fr)', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }}
      gap={6}
      w="full"
    >
      {/* Recommendation Card */}
      <MotionGridItem
        colSpan={{ base: 1, md: 2, lg: 3 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box
          p={6}
          bg="red.600"
          borderRadius="xl"
          border="1px solid"
          borderColor="red.500"
          h="full"
        >
          <VStack spacing={4} align="start">
            <HStack spacing={3} w="full" justify="space-between">
              <HStack>
                <Icon
                  as={getPricingIcon(recommendation.pricing_strategy)}
                  w={8}
                  h={8}
                  color="white"
                />
                <Heading size="lg" color="white">
                  🚨 URGENT RECOMMENDATIONS
                </Heading>
              </HStack>
              <Badge
                colorScheme={
                  recommendation.confidence >= 80
                    ? 'green'
                    : recommendation.confidence >= 60
                    ? 'yellow'
                    : 'red'
                }
                fontSize="md"
                p={2}
                borderRadius="md"
              >
                {recommendation.confidence}% Confidence
              </Badge>
            </HStack>

            <Box
              bg="whiteAlpha.100"
              p={4}
              borderRadius="md"
              w="full"
            >
              <Text fontSize="xl" fontWeight="bold" color="white" mb={4}>
                {recommendation.explanation}
              </Text>
              
              <VStack align="start" spacing={3}>
                {recommendation.suggested_actions.map((action, index) => (
                  <HStack key={index} spacing={3}>
                    <Icon as={FaExclamationTriangle} color="yellow.300" w={5} h={5} />
                    <Text color="white" fontSize="lg">
                      {action}
                    </Text>
                  </HStack>
                ))}
              </VStack>
            </Box>

            {market_data.price_range && (
              <Box
                bg="whiteAlpha.100"
                p={4}
                borderRadius="md"
                w="full"
              >
                <Text fontSize="lg" color="white" mb={2}>
                  💰 RECOMMENDED PRICE RANGE
                </Text>
                <HStack w="full" justify="space-between" mb={2}>
                  <Stat>
                    <StatLabel color="gray.300">Minimum</StatLabel>
                    <StatNumber color="white" fontSize="2xl">
                      {formatPrice(market_data.price_range.min, location)}
                    </StatNumber>
                  </Stat>
                  <Stat>
                    <StatLabel color="gray.300">Maximum</StatLabel>
                    <StatNumber color="white" fontSize="2xl">
                      {formatPrice(market_data.price_range.max, location)}
                    </StatNumber>
                  </Stat>
                </HStack>
                <Progress
                  value={50}
                  w="full"
                  borderRadius="full"
                  colorScheme="yellow"
                  size="sm"
                />
              </Box>
            )}
          </VStack>
        </Box>
      </MotionGridItem>

      {/* Real-time Factors Card */}
      <MotionGridItem
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Box
          p={6}
          bg={cardBg}
          borderRadius="xl"
          border="1px solid"
          borderColor={borderColor}
          h="full"
        >
          <VStack spacing={4} align="start">
            <HStack spacing={3}>
              <Icon as={FaChartLine} w={6} h={6} color="blue.400" />
              <Heading size="md" color={textColor}>
                Real-time Factors
              </Heading>
            </HStack>
            
            <Box w="full" h="200px">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={realTimeFactors}>
                  <PolarGrid stroke={borderColor} />
                  <PolarAngleAxis
                    dataKey="factor"
                    tick={{ fill: textColor }}
                  />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar
                    name="Impact"
                    dataKey="value"
                    stroke="#3182CE"
                    fill="#3182CE"
                    fillOpacity={0.6}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          </VStack>
        </Box>
      </MotionGridItem>

      {/* Peak Hours Card */}
      <MotionGridItem
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Box
          p={6}
          bg={cardBg}
          borderRadius="xl"
          border="1px solid"
          borderColor={borderColor}
          h="full"
        >
          <VStack spacing={4} align="start">
            <HStack spacing={3}>
              <Icon as={FaClock} w={6} h={6} color="purple.400" />
              <Heading size="md" color={textColor}>
                Peak Hours
              </Heading>
            </HStack>
            <Box w="full" h="200px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={peakHoursData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={borderColor} />
                  <XAxis
                    dataKey="hour"
                    tick={{ fill: textColor }}
                  />
                  <YAxis
                    tick={{ fill: textColor }}
                    domain={[0, 100]}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: cardBg, border: 'none' }}
                    labelStyle={{ color: textColor }}
                  />
                  <Line
                    type="monotone"
                    dataKey="demand"
                    stroke="#805AD5"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </VStack>
        </Box>
      </MotionGridItem>

      {/* Market Position Card */}
      <MotionGridItem
        colSpan={{ base: 1, md: 2, lg: 1 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Box
          p={6}
          bg={cardBg}
          borderRadius="xl"
          border="1px solid"
          borderColor={borderColor}
          h="full"
        >
          <VStack spacing={4} align="start">
            <HStack spacing={3}>
              <Icon as={FaChartBar} w={6} h={6} color="green.400" />
              <Heading size="md" color={textColor}>
                Market Position
              </Heading>
            </HStack>
            <Stat>
              <StatLabel color="gray.400">Average Rating</StatLabel>
              <StatNumber color={textColor}>
                {market_data.average_competitor_rating.toFixed(1)}
              </StatNumber>
              <StatHelpText color="gray.400">
                <StatArrow
                  type={market_data.average_competitor_rating > 4 ? 'increase' : 'decrease'}
                />
                vs Industry Average
              </StatHelpText>
            </Stat>
            <Box w="full" h="150px">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={competitorRatings}>
                  <defs>
                    <linearGradient id="ratingGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#48BB78" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#48BB78" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" hide />
                  <YAxis hide domain={[0, 5]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: cardBg, border: 'none' }}
                    labelStyle={{ color: textColor }}
                  />
                  <Area
                    type="monotone"
                    dataKey="rating"
                    stroke="#48BB78"
                    fillOpacity={1}
                    fill="url(#ratingGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </VStack>
        </Box>
      </MotionGridItem>

      {/* Price Distribution Card */}
      <MotionGridItem
        colSpan={{ base: 1, md: 2, lg: 2 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Box
          p={6}
          bg={cardBg}
          borderRadius="xl"
          border="1px solid"
          borderColor={borderColor}
          h="full"
        >
          <VStack spacing={4} align="start">
            <HStack spacing={3}>
              <Icon as={FaUsers} w={6} h={6} color="yellow.400" />
              <Heading size="md" color={textColor}>
                Price Distribution
              </Heading>
            </HStack>
            <Box w="full" h="200px">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={priceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={borderColor} />
                  <XAxis
                    dataKey="priceLevel"
                    tick={{ fill: textColor }}
                  />
                  <YAxis tick={{ fill: textColor }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: cardBg, border: 'none' }}
                    labelStyle={{ color: textColor }}
                  />
                  <Bar dataKey="count" fill="#ECC94B" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </VStack>
        </Box>
      </MotionGridItem>

      {/* Actions Card */}
      <MotionGridItem
        colSpan={{ base: 1, md: 2, lg: 3 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Box
          p={6}
          bg={cardBg}
          borderRadius="xl"
          border="1px solid"
          borderColor={borderColor}
        >
          <VStack spacing={4} align="start">
            <Heading size="md" color={textColor}>
              Recommended Actions
            </Heading>
            <Grid
              templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }}
              gap={4}
              w="full"
            >
              {recommendation.suggested_actions.map((action, index) => (
                <MotionBox
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 * index }}
                  p={4}
                  bg="gray.700"
                  borderRadius="lg"
                  border="1px solid"
                  borderColor="gray.600"
                >
                  <Text color={textColor}>{action}</Text>
                </MotionBox>
              ))}
            </Grid>
          </VStack>
        </Box>
      </MotionGridItem>
    </Grid>
  );
}
