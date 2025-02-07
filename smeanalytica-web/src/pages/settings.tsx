import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Divider,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Switch,
  Text,
  useColorModeValue,
  VStack,
  HStack,
  Avatar,
  IconButton
} from '@chakra-ui/react';
import { NextPage } from 'next';
import Layout from '../components/Layout';
import { useState } from 'react';

const SettingsCard = ({ title, description, children }: { title: string; description: string; children: React.ReactNode }) => {
  const bgColor = useColorModeValue('white', 'gray.800');

  return (
    <Card bg={bgColor} {...useColorModeValue({ shadow: 'sm' }, { borderWidth: '1px' })}>
      <CardHeader>
        <Heading size="md">{title}</Heading>
        <Text mt={1} color="gray.600" fontSize="sm">
          {description}
        </Text>
      </CardHeader>
      <Divider />
      <CardBody>{children}</CardBody>
    </Card>
  );
};

const Settings: NextPage = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = () => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  return (
    <Layout>
      <Box py={8}>
        <Stack spacing={8}>
          <Box>
            <Heading size="lg" mb={2}>Settings</Heading>
            <Text color="gray.600">Manage your account settings and preferences.</Text>
          </Box>

          <VStack spacing={6} align="stretch">
            <SettingsCard
              title="Profile Information"
              description="Update your profile information and email address."
            >
              <Stack spacing={6}>
                <HStack spacing={6}>
                  <Avatar size="xl" name="John Doe" src="/placeholder-avatar.jpg" />
                  <Box>
                    <Button size="sm" colorScheme="brand">
                      Change Photo
                    </Button>
                    <Text mt={2} fontSize="sm" color="gray.500">
                      JPG, GIF or PNG. Max size of 800K
                    </Text>
                  </Box>
                </HStack>

                <FormControl>
                  <FormLabel>Full Name</FormLabel>
                  <Input defaultValue="John Doe" />
                </FormControl>

                <FormControl>
                  <FormLabel>Email Address</FormLabel>
                  <Input defaultValue="john.doe@example.com" type="email" />
                </FormControl>

                <FormControl>
                  <FormLabel>Company</FormLabel>
                  <Input defaultValue="Acme Inc." />
                </FormControl>
              </Stack>
            </SettingsCard>

            <SettingsCard
              title="Notifications"
              description="Choose what notifications you want to receive."
            >
              <Stack spacing={4}>
                <FormControl display="flex" alignItems="center">
                  <Switch id="email-alerts" defaultChecked />
                  <FormLabel htmlFor="email-alerts" mb="0" ml={3}>
                    Email Alerts
                  </FormLabel>
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <Switch id="push-notifications" defaultChecked />
                  <FormLabel htmlFor="push-notifications" mb="0" ml={3}>
                    Push Notifications
                  </FormLabel>
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <Switch id="monthly-report" defaultChecked />
                  <FormLabel htmlFor="monthly-report" mb="0" ml={3}>
                    Monthly Report Summary
                  </FormLabel>
                </FormControl>
              </Stack>
            </SettingsCard>

            <SettingsCard
              title="Security"
              description="Update your security preferences."
            >
              <Stack spacing={4}>
                <FormControl>
                  <FormLabel>Current Password</FormLabel>
                  <Input type="password" />
                </FormControl>

                <FormControl>
                  <FormLabel>New Password</FormLabel>
                  <Input type="password" />
                </FormControl>

                <FormControl>
                  <FormLabel>Confirm New Password</FormLabel>
                  <Input type="password" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <Switch id="two-factor" />
                  <FormLabel htmlFor="two-factor" mb="0" ml={3}>
                    Enable Two-Factor Authentication
                  </FormLabel>
                </FormControl>
              </Stack>
            </SettingsCard>

            <Box>
              <Button
                colorScheme="brand"
                size="lg"
                isLoading={isLoading}
                onClick={handleSave}
              >
                Save Changes
              </Button>
            </Box>
          </VStack>
        </Stack>
      </Box>
    </Layout>
  );
};

export default Settings; 