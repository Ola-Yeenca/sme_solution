import { Box, Container, Flex, HStack, Link as ChakraLink, Button, useColorModeValue } from '@chakra-ui/react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const router = useRouter();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const navItems = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Analytics', href: '/analytics' },
    { label: 'Reports', href: '/reports' },
    { label: 'Settings', href: '/settings' },
  ];

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
      <Box
        as="header"
        position="fixed"
        w="full"
        bg={bgColor}
        borderBottom="1px"
        borderColor={borderColor}
        py={4}
        px={8}
        zIndex={10}
      >
        <Container maxW="container.xl">
          <Flex justify="space-between" align="center">
            <Link href="/dashboard" passHref>
              <ChakraLink
                fontSize="2xl"
                fontWeight="bold"
                _hover={{ textDecoration: 'none' }}
              >
                SMEAnalytica
              </ChakraLink>
            </Link>

            <HStack spacing={8}>
              <HStack spacing={4} display={{ base: 'none', md: 'flex' }}>
                {navItems.map((item) => (
                  <Link key={item.href} href={item.href} passHref>
                    <ChakraLink
                      px={3}
                      py={2}
                      rounded="md"
                      color={router.pathname === item.href ? 'brand.500' : 'gray.600'}
                      fontWeight={router.pathname === item.href ? 'semibold' : 'medium'}
                      _hover={{
                        textDecoration: 'none',
                        color: 'brand.500',
                        bg: 'gray.50'
                      }}
                    >
                      {item.label}
                    </ChakraLink>
                  </Link>
                ))}
              </HStack>

              <Button variant="solid" colorScheme="brand">
                Get Started
              </Button>
            </HStack>
          </Flex>
        </Container>
      </Box>

      <Box as="main" pt="80px" pb={20}>
        <Container maxW="container.xl">
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout; 