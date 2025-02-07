 import { Container, Heading } from '@chakra-ui/react';
import BusinessForm from '../components/BusinessForm';

export default function Home() {
  return (
    <Container maxW="container.md" py={8}>
      <Heading as="h1" mb={6}>
        SME Business Analysis
      </Heading>
      <BusinessForm />
    </Container>
  );
}