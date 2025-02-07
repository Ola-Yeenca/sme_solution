import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Button } from 'react-native-paper';

const DashboardScreen = ({ navigation }: any) => {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Business Analytics</Title>
          <Paragraph>View detailed analytics about your business performance</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button onPress={() => navigation.navigate('Analytics')}>
            View Analytics
          </Button>
        </Card.Actions>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Market Insights</Title>
          <Paragraph>Understand your market position and competition</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button onPress={() => navigation.navigate('Analytics', { section: 'market' })}>
            View Insights
          </Button>
        </Card.Actions>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Customer Sentiment</Title>
          <Paragraph>Track and analyze customer feedback</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button onPress={() => navigation.navigate('Analytics', { section: 'sentiment' })}>
            View Sentiment
          </Button>
        </Card.Actions>
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f6fa',
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
});

export default DashboardScreen;
