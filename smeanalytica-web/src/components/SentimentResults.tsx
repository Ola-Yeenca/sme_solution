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
} from '@chakra-ui/react';
import { FaSmile, FaMeh, FaFrown } from 'react-icons/fa';
import { motion } from 'framer-motion';

const MotionBox = motion(Box);

interface SentimentMetrics {
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
  average_rating: number;
  total_reviews: number;
  sentiment_trend: 'improving' | 'declining' | 'stable';
}

interface SentimentData {
  overall_sentiment: number;
  key_topics: Array<{
    topic: string;
    sentiment: number;
    frequency: number;
  }>;
  recent_trends: Array<{
    date: string;
    sentiment: number;
  }>;
}

interface SentimentResultsProps {
  status: string;
  sentiment_data?: SentimentData;
  metrics?: SentimentMetrics;
}

export function SentimentResults({ status, sentiment_data, metrics }: SentimentResultsProps) {
  if (status !== 'success' || !sentiment_data || !metrics) {
    return (
      <Box p={5}>
        <Text>No sentiment data available</Text>
      </Box>
    );
  }

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment >= 0.7) return FaSmile;
    if (sentiment <= 0.3) return FaFrown;
    return FaMeh;
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment >= 0.7) return 'green.500';
    if (sentiment <= 0.3) return 'red.500';
    return 'yellow.500';
  };

  return (
    <Grid
      templateColumns="repeat(12, 1fr)"
      gap={6}
      p={5}
    >
      {/* Overall Sentiment */}
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
            <Heading size="md">Overall Sentiment</Heading>
            <Box textAlign="center">
              <Text fontSize="6xl" color={getSentimentColor(sentiment_data.overall_sentiment)}>
                {(sentiment_data.overall_sentiment * 100).toFixed(1)}%
              </Text>
              <Progress
                value={sentiment_data.overall_sentiment * 100}
                colorScheme={sentiment_data.overall_sentiment >= 0.7 ? 'green' : sentiment_data.overall_sentiment <= 0.3 ? 'red' : 'yellow'}
                size="sm"
                mt={2}
              />
            </Box>
          </VStack>
        </MotionBox>
      </GridItem>

      {/* Metrics */}
      <GridItem colSpan={[12, 6, 8]}>
        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
          <Stat>
            <StatLabel>Positive Reviews</StatLabel>
            <StatNumber>{metrics.positive_percentage}%</StatNumber>
            <StatHelpText>
              <Badge colorScheme="green">Positive</Badge>
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Neutral Reviews</StatLabel>
            <StatNumber>{metrics.neutral_percentage}%</StatNumber>
            <StatHelpText>
              <Badge colorScheme="yellow">Neutral</Badge>
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Negative Reviews</StatLabel>
            <StatNumber>{metrics.negative_percentage}%</StatNumber>
            <StatHelpText>
              <Badge colorScheme="red">Negative</Badge>
            </StatHelpText>
          </Stat>
        </Grid>
      </GridItem>

      {/* Key Topics */}
      <GridItem colSpan={12}>
        <VStack align="stretch" spacing={4}>
          <Heading size="md">Key Topics</Heading>
          {sentiment_data.key_topics.map((topic, index) => (
            <Box key={index} p={4} bg="gray.700" borderRadius="md">
              <HStack justify="space-between">
                <Text>{topic.topic}</Text>
                <HStack>
                  <Badge colorScheme={getSentimentColor(topic.sentiment) === 'green.500' ? 'green' : getSentimentColor(topic.sentiment) === 'red.500' ? 'red' : 'yellow'}>
                    {(topic.sentiment * 100).toFixed(1)}%
                  </Badge>
                  <Text fontSize="sm" color="gray.400">
                    {topic.frequency} mentions
                  </Text>
                </HStack>
              </HStack>
              <Progress
                value={topic.sentiment * 100}
                colorScheme={topic.sentiment >= 0.7 ? 'green' : topic.sentiment <= 0.3 ? 'red' : 'yellow'}
                size="sm"
                mt={2}
              />
            </Box>
          ))}
        </VStack>
      </GridItem>
    </Grid>
  );
}
