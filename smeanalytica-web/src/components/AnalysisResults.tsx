import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  Button,
  Icon,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Grid,
} from '@chakra-ui/react';
import { RepeatIcon } from '@chakra-ui/icons';

// Data structure interfaces
interface MarketData {
  average_competitor_rating: number;
  market_position: string;
  average_competitor_price_level: string;
}

interface Recommendation {
  pricing_strategy: 'increase' | 'decrease' | 'maintain';
  confidence: number;
  explanation: string;
  suggested_actions: string[];
}

interface DynamicPricingData {
  market_data: MarketData;
  recommendation: Recommendation;
}

interface SentimentData {
  sentiment_analysis: {
    overall_sentiment: string;
    sentiment_scores: {
      positive: number;
      neutral: number;
      negative: number;
    };
    key_findings: string[];
    sentiment_trends?: {
      trend: string;
      score: number;
    }[];
    review_highlights?: {
      positive: string[];
      negative: string[];
    };
  };
}

interface CompetitionData {
  competition: {
    strengths: string[];
    weaknesses: string[];
    market_position_analysis: string;
    recommendations: string[];
  };
}

interface MarketAnalysisData {
  market: {
    market_size: string | number;
    growth_rate: number;
    market_share: number;
    trends: string[];
    opportunities: string[];
  };
}

interface BasicPricingData {
  pricing: {
    recommended_base_price: number;
    min_price: number;
    max_price: number;
    factors: string[];
    recommendations: string[];
  };
}

// Component props interfaces
interface DynamicPricingProps {
  market_data: MarketData;
  recommendation: Recommendation;
}

interface SentimentAnalysisProps {
  data: SentimentData;
}

interface CompetitionAnalysisProps {
  data: CompetitionData;
}

interface MarketAnalysisProps {
  data: MarketAnalysisData;
}

interface BasicPricingProps {
  data: BasicPricingData;
}

interface AnalysisResponse {
  success: boolean;
  data?: DynamicPricingData | SentimentData | CompetitionData | MarketAnalysisData | BasicPricingData;
  error?: string;
}

interface AnalysisResultsProps {
  data: AnalysisResponse;
  analysisType: 'dynamic_pricing' | 'sentiment' | 'competition' | 'market' | 'pricing';
}

const DynamicPricingResults: React.FC<DynamicPricingProps> = ({ market_data, recommendation }) => {
  if (!market_data || !recommendation) {
    return (
      <Box p={4}>
        <Text color="red.500">
          Dynamic pricing analysis data is incomplete
        </Text>
      </Box>
    );
  }

  return (
    <>
      <Box>
        <Heading size="md" mb={4}>Market Analysis</Heading>
        <SimpleGrid columns={2} spacing={4}>
          <Box>
            <Text fontWeight="bold">Average Competitor Rating:</Text>
            <Text>{market_data.average_competitor_rating?.toFixed(1) || 'N/A'} / 5.0</Text>
          </Box>
          <Box>
            <Text fontWeight="bold">Market Position:</Text>
            <Text>{market_data.market_position || 'Unknown'}</Text>
          </Box>
          <Box colSpan={2}>
            <Text fontWeight="bold">Average Price Level:</Text>
            <Text>{market_data.average_competitor_price_level || 'N/A'}</Text>
          </Box>
        </SimpleGrid>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Dynamic Pricing Recommendations</Heading>
        <VStack spacing={4} align="stretch">
          <Box>
            <Text fontWeight="bold">Pricing Strategy:</Text>
            <Text>
              {(recommendation.pricing_strategy || 'UNKNOWN').toUpperCase()}
            </Text>
            <Text>Confidence: {((recommendation.confidence || 0) * 100).toFixed(1)}%</Text>
          </Box>
          <Box>
            <Text fontWeight="bold">Explanation:</Text>
            <Text>{recommendation.explanation || 'No explanation available'}</Text>
          </Box>
          <Box>
            <Text fontWeight="bold">Suggested Actions:</Text>
            <VStack spacing={2} align="stretch" mt={2}>
              {(recommendation.suggested_actions || []).map((action, index) => (
                <Text key={index}>• {action}</Text>
              ))}
            </VStack>
          </Box>
        </VStack>
      </Box>
    </>
  );
};

const SentimentAnalysisResults: React.FC<SentimentAnalysisProps> = ({ data }) => {
  if (!data?.sentiment_analysis) {
    return (
      <Alert status="warning">
        <AlertIcon />
        <AlertTitle>Missing Data</AlertTitle>
        <AlertDescription>Sentiment analysis data is incomplete</AlertDescription>
      </Alert>
    );
  }

  const { sentiment_analysis } = data;
  const scores = sentiment_analysis.sentiment_scores || { positive: 0, neutral: 0, negative: 0 };
  const overallSentiment = sentiment_analysis.overall_sentiment?.toLowerCase() || 'neutral';

  return (
    <Box>
      <Heading size="md" mb={4}>Sentiment Analysis</Heading>
      <VStack spacing={6} align="stretch">
        <Box>
          <Text fontWeight="bold" mb={2}>Overall Sentiment</Text>
          <Progress 
            value={scores.positive * 100} 
            colorScheme={overallSentiment === 'positive' ? 'green' : overallSentiment === 'negative' ? 'red' : 'yellow'}
            size="lg"
            mb={2}
          />
          <Badge 
            colorScheme={overallSentiment === 'positive' ? 'green' : overallSentiment === 'negative' ? 'red' : 'yellow'}
            fontSize="md"
            px={3}
            py={1}
          >
            {sentiment_analysis.overall_sentiment?.toUpperCase() || 'NEUTRAL'}
          </Badge>
        </Box>
        
        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
          <Stat>
            <StatLabel>Positive</StatLabel>
            <StatNumber>{(scores.positive * 100).toFixed(1)}%</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Neutral</StatLabel>
            <StatNumber>{(scores.neutral * 100).toFixed(1)}%</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Negative</StatLabel>
            <StatNumber>{(scores.negative * 100).toFixed(1)}%</StatNumber>
          </Stat>
        </Grid>

        {sentiment_analysis.key_findings && sentiment_analysis.key_findings.length > 0 && (
          <Box>
            <Text fontWeight="bold" mb={2}>Key Findings</Text>
            <VStack spacing={2} align="stretch">
              {sentiment_analysis.key_findings.map((finding, index) => (
                <Text key={index}>• {finding}</Text>
              ))}
            </VStack>
          </Box>
        )}

        {sentiment_analysis.review_highlights && (
          <Grid templateColumns="repeat(2, 1fr)" gap={4}>
            <Box p={4} borderWidth="1px" borderRadius="md" bg="green.50">
              <Heading size="sm" mb={3} color="green.600">Positive Highlights</Heading>
              <VStack align="stretch" spacing={2}>
                {sentiment_analysis.review_highlights.positive.map((highlight, index) => (
                  <Text key={index} color="green.600">• {highlight}</Text>
                ))}
              </VStack>
            </Box>
            <Box p={4} borderWidth="1px" borderRadius="md" bg="red.50">
              <Heading size="sm" mb={3} color="red.600">Negative Highlights</Heading>
              <VStack align="stretch" spacing={2}>
                {sentiment_analysis.review_highlights.negative.map((highlight, index) => (
                  <Text key={index} color="red.600">• {highlight}</Text>
                ))}
              </VStack>
            </Box>
          </Grid>
        )}

        {sentiment_analysis.sentiment_trends && sentiment_analysis.sentiment_trends.length > 0 && (
          <Box>
            <Text fontWeight="bold" mb={2}>Sentiment Trends</Text>
            <VStack spacing={2} align="stretch">
              {sentiment_analysis.sentiment_trends.map((trend, index) => (
                <Box key={index} display="flex" alignItems="center" justifyContent="space-between">
                  <Text>{trend.trend}</Text>
                  <Badge 
                    colorScheme={trend.score > 0.6 ? 'green' : trend.score < 0.4 ? 'red' : 'yellow'}
                  >
                    {(trend.score * 100).toFixed(1)}%
                  </Badge>
                </Box>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

const CompetitionAnalysisResults: React.FC<CompetitionAnalysisProps> = ({ data }) => {
  if (!data?.competition) {
    return (
      <Box p={4}>
        <Text color="red.500">
          Competition analysis data is incomplete
        </Text>
      </Box>
    );
  }

  const { competition } = data;

  return (
    <Box>
      <Heading size="md" mb={4}>Competition Analysis</Heading>
      <VStack spacing={4} align="stretch">
        <SimpleGrid columns={2} spacing={4}>
          <Box p={4} borderWidth="1px" borderRadius="md">
            <Heading size="sm" mb={3}>Strengths</Heading>
            <VStack align="stretch" spacing={2}>
              {(competition.strengths || []).map((strength, index) => (
                <Text key={index}>• {strength}</Text>
              ))}
            </VStack>
          </Box>
          <Box p={4} borderWidth="1px" borderRadius="md">
            <Heading size="sm" mb={3}>Weaknesses</Heading>
            <VStack align="stretch" spacing={2}>
              {(competition.weaknesses || []).map((weakness, index) => (
                <Text key={index}>• {weakness}</Text>
              ))}
            </VStack>
          </Box>
        </SimpleGrid>
        
        <Box>
          <Text fontWeight="bold" mb={2}>Market Position</Text>
          <Text>{competition.market_position_analysis || 'No market position analysis available'}</Text>
        </Box>

        <Box>
          <Text fontWeight="bold" mb={2}>Recommendations</Text>
          <VStack spacing={2} align="stretch">
            {(competition.recommendations || []).map((rec, index) => (
              <Text key={index}>• {rec}</Text>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

const MarketAnalysisResults: React.FC<MarketAnalysisProps> = ({ data }) => {
  if (!data?.market) {
    return (
      <Box p={4}>
        <Text color="red.500">
          Market analysis data is incomplete
        </Text>
      </Box>
    );
  }

  const { market } = data;

  return (
    <Box>
      <Heading size="md" mb={4}>Market Analysis</Heading>
      <VStack spacing={4} align="stretch">
        <SimpleGrid columns={2} spacing={4}>
          <Stat>
            <StatLabel>Market Size</StatLabel>
            <StatNumber>{market.market_size || 'N/A'}</StatNumber>
            <StatHelpText>
              <StatArrow type={(market.growth_rate || 0) > 0 ? 'increase' : 'decrease'} />
              {market.growth_rate || 0}% YoY
            </StatHelpText>
          </Stat>
          <Stat>
            <StatLabel>Market Share</StatLabel>
            <StatNumber>{market.market_share || 0}%</StatNumber>
          </Stat>
        </SimpleGrid>

        <Box>
          <Text fontWeight="bold" mb={2}>Market Trends</Text>
          <VStack spacing={2} align="stretch">
            {(market.trends || []).map((trend, index) => (
              <Text key={index}>• {trend}</Text>
            ))}
          </VStack>
        </Box>

        <Box>
          <Text fontWeight="bold" mb={2}>Opportunities</Text>
          <VStack spacing={2} align="stretch">
            {(market.opportunities || []).map((opportunity, index) => (
              <Text key={index}>• {opportunity}</Text>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

const BasicPricingResults: React.FC<BasicPricingProps> = ({ data }) => {
  if (!data?.pricing) {
    return (
      <Box p={4}>
        <Text color="red.500">
          Basic pricing analysis data is incomplete
        </Text>
      </Box>
    );
  }

  const { pricing } = data;

  return (
    <Box>
      <Heading size="md" mb={4}>Basic Pricing Analysis</Heading>
      <VStack spacing={4} align="stretch">
        <SimpleGrid columns={2} spacing={4}>
          <Stat>
            <StatLabel>Recommended Base Price</StatLabel>
            <StatNumber>${pricing.recommended_base_price || 'N/A'}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Price Range</StatLabel>
            <StatNumber>
              ${pricing.min_price || 'N/A'} - ${pricing.max_price || 'N/A'}
            </StatNumber>
          </Stat>
        </SimpleGrid>

        <Box>
          <Text fontWeight="bold" mb={2}>Price Factors</Text>
          <VStack spacing={2} align="stretch">
            {(pricing.factors || []).map((factor, index) => (
              <Text key={index}>• {factor}</Text>
            ))}
          </VStack>
        </Box>

        <Box>
          <Text fontWeight="bold" mb={2}>Recommendations</Text>
          <VStack spacing={2} align="stretch">
            {(pricing.recommendations || []).map((rec, index) => (
              <Text key={index}>• {rec}</Text>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Box>
  );
};

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data, analysisType }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
        const headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'  // Force backend refresh
        };
        
        const response = await axios.post('/api/analysis/analyze', {
            ...data,
            analysis_type: analysisType,
            force_refresh: true  // Signal backend to refresh data
        }, { headers });
        
        if (response.data.success) {
            setResults(response.data.data);
        } else {
            setError(response.data.error || 'Analysis failed');
        }
    } catch (err: any) {
        setError(err.message || 'Failed to fetch analysis results');
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    if (analysisType) {
        fetchAnalysis();
    }
  }, [analysisType, data]);

  const handleRefresh = async () => {
    await fetchAnalysis();
  };

  if (!data?.success || !data?.data) {
    return (
      <Box p={4}>
        <Text color="red.500">
          {data?.error || 'No analysis data available'}
        </Text>
      </Box>
    );
  }

  const analysisData = results || data.data;

  const renderAnalysisContent = () => {
    switch (analysisType) {
      case 'dynamic_pricing':
        return <DynamicPricingResults market_data={analysisData.market_data} recommendation={analysisData.recommendation} />;
      case 'sentiment':
        return <SentimentAnalysisResults data={analysisData} />;
      case 'competition':
        return <CompetitionAnalysisResults data={analysisData} />;
      case 'market':
        return <MarketAnalysisResults data={analysisData} />;
      case 'pricing':
        return <BasicPricingResults data={analysisData} />;
      default:
        return (
          <Box p={4}>
            <Text color="red.500">
              The selected analysis type is not supported
            </Text>
          </Box>
        );
    }
  };

  return (
    <Box mt={8} p={6} borderWidth="1px" borderRadius="lg" bg="white">
      <VStack spacing={6} align="stretch">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Heading size="lg">
            {analysisType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')} Results
          </Heading>
          <Button 
            onClick={handleRefresh}
            leftIcon={<Icon as={RepeatIcon} />}
            colorScheme="blue"
            isLoading={loading}
            loadingText="Refreshing..."
          >
            Refresh Analysis
          </Button>
        </Box>
        {renderAnalysisContent()}
      </VStack>
    </Box>
  );
};

export default AnalysisResults;
