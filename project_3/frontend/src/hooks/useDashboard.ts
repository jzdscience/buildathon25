import { useState, useEffect, useCallback } from 'react';
import { DashboardData, UseDashboardReturn } from '../types';
import { apiClient, formatApiError } from '../services/api';

const useDashboard = (
  days: number = 7, 
  autoRefresh: boolean = true, 
  refreshInterval: number = 60000 // 1 minute
): UseDashboardReturn => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.dashboard.getDashboardData(days);
      
      if (response.success && response.data) {
        setData(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, [days]);

  // Initial load
  useEffect(() => {
    refresh();
  }, [refresh]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) return;

    const intervalId = setInterval(refresh, refreshInterval);
    
    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, refresh]);

  // Listen for visibility change to refresh when user comes back
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && autoRefresh) {
        refresh();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [autoRefresh, refresh]);

  return {
    data,
    loading,
    error,
    refresh,
  };
};

export default useDashboard;

