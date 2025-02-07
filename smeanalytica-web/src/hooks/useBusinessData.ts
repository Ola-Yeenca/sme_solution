import { useState, useEffect } from 'react';
import { businessApi, BusinessMetrics } from '../services/api';

interface UseBusinessDataResult {
  metrics: BusinessMetrics | null;
  analytics: any | null;
  sentiment: any | null;
  loading: boolean;
  error: Error | null;
}

export function useBusinessData(businessName: string): UseBusinessDataResult {
  const [metrics, setMetrics] = useState<BusinessMetrics | null>(null);
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [sentiment, setSentiment] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        const [metricsData, analyticsData, sentimentData] = await Promise.all([
          businessApi.getMetrics(businessName),
          businessApi.getAnalytics(businessName),
          businessApi.getSentimentAnalysis(businessName),
        ]);

        setMetrics(metricsData);
        setAnalytics(analyticsData);
        setSentiment(sentimentData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('An error occurred'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [businessName]);

  return { metrics, analytics, sentiment, loading, error };
}
