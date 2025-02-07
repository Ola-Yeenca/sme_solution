import React, { useState, useCallback } from 'react';
import {
  Box,
  SimpleGrid,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  Stack,
  Select,
  useColorModeValue,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { NextPage } from 'next';
import Layout from '../components/Layout';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsCard = ({ title, children }: { title: string; children: React.ReactNode }) => {
  const bgColor = useColorModeValue('white', 'gray.800');

  return (
    <Card bg={bgColor} {...useColorModeValue({ shadow: 'sm' }, { borderWidth: '1px' })}>
      <CardHeader>
        <Heading size="md">{title}</Heading>
      </CardHeader>
      <CardBody>{children}</CardBody>
    </Card>
  );
};

const Analytics: NextPage = () => {
  // Sample data for the charts
  const revenueData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [30000, 35000, 32000, 38000, 42000, 45000],
        borderColor: 'rgb(14, 99, 255)',
        backgroundColor: 'rgba(14, 99, 255, 0.1)',
        fill: true,
      },
    ],
  };

  const userActivityData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Active Users',
        data: [120, 150, 180, 160, 140, 90, 95],
        backgroundColor: 'rgba(14, 99, 255, 0.8)',
      },
    ],
  };

  const customerSegmentationData = {
    labels: ['Enterprise', 'SMB', 'Startup', 'Individual'],
    datasets: [
      {
        data: [35, 30, 20, 15],
        backgroundColor: [
          'rgba(14, 99, 255, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  const [analysisType, setAnalysisType] = useState('revenue');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalysisTypeChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newAnalysisType = e.target.value;
    setAnalysisType(newAnalysisType);
    // Only perform analysis if we have all required data
    if (newAnalysisType) {
      await performAnalysis();
    }
  };

  const performAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      // Simulate API call
      const response = {
        data: {
          revenue: 45000,
          activeUsers: 2845,
          newCustomers: 487,
          churnRate: 2.3,
        },
      };
      setAnalysisResults(response.data);
    } catch (error) {
      console.error(error);
      setAnalysisResults(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <Layout>
      <Box py={8}>
        <Stack spacing={8}>
          <Box>
            <Heading size="lg" mb={2}>Analytics</Heading>
            <Text color="gray.600">Track your business performance and growth.</Text>
          </Box>

          <Box>
            <Select maxW="200px" mb={6} value={analysisType} onChange={handleAnalysisTypeChange}>
              <option value="revenue">Revenue Growth</option>
              <option value="user_activity">User Activity</option>
              <option value="customer_segmentation">Customer Segmentation</option>
            </Select>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              <AnalyticsCard title="Revenue Growth">
                <Box h="300px">
                  <Line data={revenueData} options={chartOptions} />
                </Box>
              </AnalyticsCard>

              <AnalyticsCard title="User Activity">
                <Box h="300px">
                  <Bar data={userActivityData} options={chartOptions} />
                </Box>
              </AnalyticsCard>

              <AnalyticsCard title="Customer Segmentation">
                <Box h="300px">
                  <Doughnut data={customerSegmentationData} options={chartOptions} />
                </Box>
              </AnalyticsCard>
            </SimpleGrid>
          </Box>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Total Revenue</StatLabel>
                  <StatNumber>${analysisResults?.revenue}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    23.36%
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Active Users</StatLabel>
                  <StatNumber>{analysisResults?.activeUsers}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    12.05%
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>New Customers</StatLabel>
                  <StatNumber>{analysisResults?.newCustomers}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    8.87%
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Churn Rate</StatLabel>
                  <StatNumber>{analysisResults?.churnRate}%</StatNumber>
                  <StatHelpText>
                    <StatArrow type="decrease" />
                    0.5%
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>
        </Stack>
      </Box>
    </Layout>
  );
};

export default Analytics;