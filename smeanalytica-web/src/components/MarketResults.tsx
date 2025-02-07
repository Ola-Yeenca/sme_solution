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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const MotionBox = motion(Box);

interface MarketMetrics {
  market_share: number;
  growth_potential: number;
  market_position: string;
  market_saturation: number;
  competition_intensity: number;
}

interface MarketTrend {
  date: string;
  value: number;
}

interface MarketData {
  market_size: number;
  growth_rate: number;
  trends: MarketTrend[];
  opportunities: Array<{
    type: string;
    impact: 'high' | 'medium' | 'low';
    ease: 'easy' | 'medium' | 'hard';
  }>;
}

interface MarketResultsProps {
  status: string;
  market_data?: MarketData;
  metrics?: MarketMetrics;
  location: string;
}

export function MarketResults({ status, market_data, metrics, location }: MarketResultsProps) {
  if (status !== 'success' || !market_data || !metrics) {
    return (
      <Box p={5}>
        <Text>No market data available</Text>
      </Box>
    );
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'green';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <Grid
      templateColumns="repeat(12, 1fr)"
      gap={6}
      p={5}
    >
      {/* Market Overview */}
      <GridItem colSpan={[12, 6, 3]}>
        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <VStack
            spacing={4}
            p={5}
            bg="gray.700"
            borderRadius="lg"
            align="stretch"
          >
            <Heading size="md">Market Overview</Heading>
            <Stat>
              <StatLabel>Market Size</StatLabel>
              <StatNumber>${(market_data.market_size / 1000000).toFixed(1)}M</StatNumber>
              <StatHelpText>
                <StatArrow type={market_data.growth_rate > 0 ? 'increase' : 'decrease'} />
                {market_data.growth_rate}% YoY
              </StatHelpText>
            </Stat>
          </VStack>
        </MotionBox>
      </GridItem>

      {/* Market Position */}
      <GridItem colSpan={[12, 6, 3]}>
        <VStack
          spacing={4}
          p={5}
          bg="gray.700"
          borderRadius="lg"
          align="stretch"
        >
          <Heading size="md">Market Position</Heading>
          <Text fontSize="xl" fontWeight="bold">
            {metrics.market_position}
          </Text>
          <Progress
            value={metrics.market_share * 100}
            colorScheme="blue"
            size="sm"
          />
          <Text fontSize="sm" color="gray.400">
            Market Share: {(metrics.market_share * 100).toFixed(1)}%
          </Text>
        </VStack>
      </GridItem>

      {/* Growth Potential */}
      <GridItem colSpan={[12, 6, 3]}>
        <VStack
          spacing={4}
          p={5}
          bg="gray.700"
          borderRadius="lg"
          align="stretch"
        >
          <Heading size="md">Growth Potential</Heading>
          <Text fontSize="xl" fontWeight="bold">
            {metrics.growth_potential.toFixed(1)}/10
          </Text>
          <Progress
            value={metrics.growth_potential * 10}
            colorScheme="green"
            size="sm"
          />
        </VStack>
      </GridItem>

      {/* Competition Intensity */}
      <GridItem colSpan={[12, 6, 3]}>
        <VStack
          spacing={4}
          p={5}
          bg="gray.700"
          borderRadius="lg"
          align="stretch"
        >
          <Heading size="md">Competition</Heading>
          <Text fontSize="xl" fontWeight="bold">
            {metrics.competition_intensity.toFixed(1)}/10
          </Text>
          <Progress
            value={metrics.competition_intensity * 10}
            colorScheme="red"
            size="sm"
          />
        </VStack>
      </GridItem>

      {/* Market Trends */}
      <GridItem colSpan={12}>
        <Box p={5} bg="gray.700" borderRadius="lg">
          <Heading size="md" mb={4}>Market Trends</Heading>
          <Box h="300px">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={market_data.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3182ce"
                  fill="#3182ce"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </Box>
      </GridItem>

      {/* Opportunities */}
      <GridItem colSpan={12}>
        <VStack align="stretch" spacing={4}>
          <Heading size="md">Market Opportunities</Heading>
          {market_data.opportunities.map((opportunity, index) => (
            <Box key={index} p={4} bg="gray.700" borderRadius="md">
              <HStack justify="space-between">
                <Text>{opportunity.type}</Text>
                <HStack>
                  <Badge colorScheme={getImpactColor(opportunity.impact)}>
                    {opportunity.impact} impact
                  </Badge>
                  <Badge colorScheme={getImpactColor(opportunity.ease)}>
                    {opportunity.ease} to implement
                  </Badge>
                </HStack>
              </HStack>
            </Box>
          ))}
        </VStack>
      </GridItem>
    </Grid>
  );
}
