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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Progress,
  Icon,
} from '@chakra-ui/react';
import { FaArrowUp, FaArrowDown, FaMinus } from 'react-icons/fa';
import { motion } from 'framer-motion';

const MotionBox = motion(Box);

interface CompetitorData {
  name: string;
  relative_position: 'ahead' | 'behind' | 'equal';
  key_difference: string;
  price_comparison: 'higher' | 'lower' | 'similar';
  quality_comparison: 'better' | 'worse' | 'similar';
  market_share: number;
}

interface CompetitiveMetrics {
  market_position: string;
  price_competitiveness: number;
  quality_rating: number;
  market_share: number;
  competitive_advantages: string[];
  areas_for_improvement: string[];
}

interface CompetitionResultsProps {
  status: string;
  competitor_data?: {
    competitors: CompetitorData[];
    analysis: {
      strengths: string[];
      weaknesses: string[];
      opportunities: string[];
      threats: string[];
    };
  };
  metrics?: CompetitiveMetrics;
}

export function CompetitionResults({ status, competitor_data, metrics }: CompetitionResultsProps) {
  if (status !== 'success' || !competitor_data || !metrics) {
    return (
      <Box p={5}>
        <Text>No competition data available</Text>
      </Box>
    );
  }

  const getComparisonIcon = (comparison: string) => {
    switch (comparison) {
      case 'ahead':
      case 'higher':
      case 'better':
        return <Icon as={FaArrowUp} color="green.500" />;
      case 'behind':
      case 'lower':
      case 'worse':
        return <Icon as={FaArrowDown} color="red.500" />;
      default:
        return <Icon as={FaMinus} color="gray.500" />;
    }
  };

  return (
    <Grid
      templateColumns="repeat(12, 1fr)"
      gap={6}
      p={5}
    >
      {/* Market Position Overview */}
      <GridItem colSpan={[12, 6, 4]}>
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
        </MotionBox>
      </GridItem>

      {/* Competitive Analysis */}
      <GridItem colSpan={[12, 6, 8]}>
        <VStack align="stretch" spacing={4}>
          <Heading size="md">Competitive Analysis</Heading>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Competitor</Th>
                <Th>Position</Th>
                <Th>Price</Th>
                <Th>Quality</Th>
                <Th>Market Share</Th>
              </Tr>
            </Thead>
            <Tbody>
              {competitor_data.competitors.map((competitor, index) => (
                <Tr key={index}>
                  <Td>{competitor.name}</Td>
                  <Td>
                    <HStack>
                      {getComparisonIcon(competitor.relative_position)}
                      <Text>{competitor.relative_position}</Text>
                    </HStack>
                  </Td>
                  <Td>
                    <HStack>
                      {getComparisonIcon(competitor.price_comparison)}
                      <Text>{competitor.price_comparison}</Text>
                    </HStack>
                  </Td>
                  <Td>
                    <HStack>
                      {getComparisonIcon(competitor.quality_comparison)}
                      <Text>{competitor.quality_comparison}</Text>
                    </HStack>
                  </Td>
                  <Td>{(competitor.market_share * 100).toFixed(1)}%</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </VStack>
      </GridItem>

      {/* SWOT Analysis */}
      <GridItem colSpan={12}>
        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
          <Box p={4} bg="gray.700" borderRadius="md">
            <Heading size="sm" mb={4}>Strengths</Heading>
            <VStack align="stretch">
              {competitor_data.analysis.strengths.map((strength, index) => (
                <Text key={index}>{strength}</Text>
              ))}
            </VStack>
          </Box>
          <Box p={4} bg="gray.700" borderRadius="md">
            <Heading size="sm" mb={4}>Weaknesses</Heading>
            <VStack align="stretch">
              {competitor_data.analysis.weaknesses.map((weakness, index) => (
                <Text key={index}>{weakness}</Text>
              ))}
            </VStack>
          </Box>
          <Box p={4} bg="gray.700" borderRadius="md">
            <Heading size="sm" mb={4}>Opportunities</Heading>
            <VStack align="stretch">
              {competitor_data.analysis.opportunities.map((opportunity, index) => (
                <Text key={index}>{opportunity}</Text>
              ))}
            </VStack>
          </Box>
          <Box p={4} bg="gray.700" borderRadius="md">
            <Heading size="sm" mb={4}>Threats</Heading>
            <VStack align="stretch">
              {competitor_data.analysis.threats.map((threat, index) => (
                <Text key={index}>{threat}</Text>
              ))}
            </VStack>
          </Box>
        </Grid>
      </GridItem>
    </Grid>
  );
}
