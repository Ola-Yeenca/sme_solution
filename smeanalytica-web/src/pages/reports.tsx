import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Text,
  Stack,
  SimpleGrid,
  Select,
  Input,
  FormControl,
  FormLabel,
  HStack,
  Icon,
  useColorModeValue,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
} from '@chakra-ui/react';
import { NextPage } from 'next';
import Layout from '../components/Layout';
import { FiDownload, FiFileText, FiMoreVertical, FiPieChart, FiTrendingUp, FiUsers } from 'react-icons/fi';

const ReportCard = ({ title, description, icon }: { title: string; description: string; icon: React.ReactElement }) => {
  const bgColor = useColorModeValue('white', 'gray.800');

  return (
    <Card bg={bgColor} {...useColorModeValue({ shadow: 'sm' }, { borderWidth: '1px' })}>
      <CardBody>
        <Stack spacing={4}>
          <Icon as={icon} boxSize={6} color="brand.500" />
          <Stack spacing={2}>
            <Heading size="md">{title}</Heading>
            <Text color="gray.600" fontSize="sm">
              {description}
            </Text>
          </Stack>
          <Button rightIcon={<FiDownload />} colorScheme="brand" size="sm">
            Generate Report
          </Button>
        </Stack>
      </CardBody>
    </Card>
  );
};

const Reports: NextPage = () => {
  const recentReports = [
    {
      id: 1,
      name: 'Q2 2024 Financial Report',
      type: 'Financial',
      date: '2024-03-15',
      status: 'Completed',
    },
    {
      id: 2,
      name: 'User Growth Analysis',
      type: 'Analytics',
      date: '2024-03-14',
      status: 'Completed',
    },
    {
      id: 3,
      name: 'Customer Satisfaction Survey',
      type: 'Customer',
      date: '2024-03-13',
      status: 'Processing',
    },
    {
      id: 4,
      name: 'Sales Performance Review',
      type: 'Sales',
      date: '2024-03-12',
      status: 'Completed',
    },
  ];

  return (
    <Layout>
      <Box py={8}>
        <Stack spacing={8}>
          <Box>
            <Heading size="lg" mb={2}>Reports</Heading>
            <Text color="gray.600">Generate and manage your business reports.</Text>
          </Box>

          <Card>
            <CardHeader>
              <Heading size="md">Generate New Report</Heading>
            </CardHeader>
            <CardBody>
              <Stack spacing={6}>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                  <FormControl>
                    <FormLabel>Report Type</FormLabel>
                    <Select>
                      <option value="financial">Financial Report</option>
                      <option value="analytics">Analytics Report</option>
                      <option value="customer">Customer Report</option>
                      <option value="sales">Sales Report</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Date Range</FormLabel>
                    <Select>
                      <option value="7d">Last 7 days</option>
                      <option value="30d">Last 30 days</option>
                      <option value="90d">Last quarter</option>
                      <option value="1y">Last year</option>
                      <option value="custom">Custom range</option>
                    </Select>
                  </FormControl>
                </SimpleGrid>

                <HStack>
                  <Button colorScheme="brand" leftIcon={<FiFileText />}>
                    Generate Report
                  </Button>
                  <Button variant="ghost">Cancel</Button>
                </HStack>
              </Stack>
            </CardBody>
          </Card>

          <Box>
            <Heading size="md" mb={6}>Report Templates</Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              <ReportCard
                title="Financial Overview"
                description="Complete financial analysis including revenue, expenses, and profit margins"
                icon={<FiTrendingUp />}
              />
              <ReportCard
                title="Customer Analytics"
                description="Detailed insights about customer behavior and demographics"
                icon={<FiUsers />}
              />
              <ReportCard
                title="Business Metrics"
                description="Key performance indicators and business health metrics"
                icon={<FiPieChart />}
              />
            </SimpleGrid>
          </Box>

          <Box>
            <Heading size="md" mb={6}>Recent Reports</Heading>
            <Card>
              <Table>
                <Thead>
                  <Tr>
                    <Th>Report Name</Th>
                    <Th>Type</Th>
                    <Th>Date</Th>
                    <Th>Status</Th>
                    <Th></Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {recentReports.map((report) => (
                    <Tr key={report.id}>
                      <Td fontWeight="medium">{report.name}</Td>
                      <Td>{report.type}</Td>
                      <Td>{report.date}</Td>
                      <Td>
                        <Badge
                          colorScheme={report.status === 'Completed' ? 'green' : 'yellow'}
                          rounded="full"
                          px={2}
                        >
                          {report.status}
                        </Badge>
                      </Td>
                      <Td>
                        <Menu>
                          <MenuButton
                            as={IconButton}
                            icon={<FiMoreVertical />}
                            variant="ghost"
                            size="sm"
                          />
                          <MenuList>
                            <MenuItem icon={<FiDownload />}>Download</MenuItem>
                            <MenuItem icon={<FiFileText />}>View Details</MenuItem>
                          </MenuList>
                        </Menu>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Card>
          </Box>
        </Stack>
      </Box>
    </Layout>
  );
};

export default Reports; 