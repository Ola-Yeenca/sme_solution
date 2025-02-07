import React from 'react';
import { View, ScrollView, StyleSheet, Dimensions } from 'react-native';
import { Title, Card, Paragraph } from 'react-native-paper';
import { LineChart, BarChart } from 'react-native-chart-kit';

const AnalyticsScreen = ({ route }: any) => {
  const section = route.params?.section || 'general';

  const chartConfig = {
    backgroundGradientFrom: '#fff',
    backgroundGradientTo: '#fff',
    color: (opacity = 1) => `rgba(44, 62, 80, ${opacity})`,
    strokeWidth: 2,
  };

  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        data: [20, 45, 28, 80, 99, 43],
      },
    ],
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Revenue Trends</Title>
          <LineChart
            data={data}
            width={Dimensions.get('window').width - 32}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Customer Growth</Title>
          <BarChart
            data={data}
            width={Dimensions.get('window').width - 32}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      {section === 'market' && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Market Position</Title>
            <Paragraph>Your business ranks in the top 25% of local SMEs</Paragraph>
          </Card.Content>
        </Card>
      )}

      {section === 'sentiment' && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Customer Sentiment</Title>
            <Paragraph>Overall Positive Sentiment: 85%</Paragraph>
          </Card.Content>
        </Card>
      )}
    </ScrollView>
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
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});

export default AnalyticsScreen;
