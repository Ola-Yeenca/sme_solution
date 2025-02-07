import { Box, SimpleGrid, Stat, StatLabel, StatNumber, StatHelpText, StatArrow, Text, Heading, Card, CardBody, Stack, useColorModeValue } from '@chakra-ui/react';
import Layout from '../components/Layout';
import { NextPage } from 'next';

const DashboardCard = ({ title, value, change, description }: { title: string; value: string; change?: number; description: string }) => {
  const bgColor = useColorModeValue('white', 'gray.800');

  return (
    <Card bg={bgColor} {...useColorModeValue({ shadow: 'sm' }, { borderWidth: '1px' })}>
      <CardBody>
        <Stack spacing={4}>
          <Stat>
            <StatLabel fontSize="sm" color="gray.500">{title}</StatLabel>
            <StatNumber fontSize="3xl" fontWeight="bold">{value}</StatNumber>
            {change && (
              <StatHelpText>
                <StatArrow type={change > 0 ? 'increase' : 'decrease'} />
                {Math.abs(change)}%
              </StatHelpText>
            )}
          </Stat>
          <Text fontSize="sm" color="gray.500">
            {description}
          </Text>
        </Stack>
      </CardBody>
    </Card>
  );
};

const Dashboard: NextPage = () => {
  const metrics = [
    {
      title: 'Revenue',
      value: '$48,574',
      change: 12,
      description: 'Total revenue this month'
    },
    {
      title: 'Active Users',
      value: '2,845',
      change: 7.2,
      description: 'Users active in the last 30 days'
    },
    {
      title: 'Conversion Rate',
      value: '3.24%',
      change: -2.1,
      description: 'Average conversion rate'
    },
    {
      title: 'Growth Rate',
      value: '15.7%',
      change: 4.3,
      description: 'Month over month growth'
    }
  ];

  return (
    <Layout>
      <Box py={8}>
        <Stack spacing={8}>
          <Box>
            <Heading size="lg" mb={2}>Dashboard</Heading>
            <Text color="gray.600">Welcome back! Here's an overview of your business metrics.</Text>
          </Box>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {metrics.map((metric, index) => (
              <DashboardCard
                key={index}
                title={metric.title}
                value={metric.value}
                change={metric.change}
                description={metric.description}
              />
            ))}
          </SimpleGrid>

          {/* Add more dashboard sections here */}
        </Stack>
      </Box>
    </Layout>
  );
};

export default Dashboard; 