import { useState, useEffect, useCallback } from 'react';
import { MonitoringStatus, UseMonitoringReturn } from '../types';
import { apiClient, formatApiError } from '../services/api';

const useMonitoring = (
  autoRefresh: boolean = true, 
  refreshInterval: number = 30000 // 30 seconds
): UseMonitoringReturn => {
  const [status, setStatus] = useState<MonitoringStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.monitoring.getStatus();
      
      if (response.success && response.data) {
        setStatus(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const startMonitoring = useCallback(async () => {
    try {
      setError(null);
      
      const response = await apiClient.monitoring.startMonitoring();
      
      if (response.success) {
        // Refresh status after starting
        await refresh();
      } else if (response.error) {
        setError(response.error);
        throw new Error(response.error);
      }
    } catch (err) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, [refresh]);

  const stopMonitoring = useCallback(async () => {
    try {
      setError(null);
      
      const response = await apiClient.monitoring.stopMonitoring();
      
      if (response.success) {
        // Refresh status after stopping
        await refresh();
      } else if (response.error) {
        setError(response.error);
        throw new Error(response.error);
      }
    } catch (err) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, [refresh]);

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

  return {
    status,
    loading,
    error,
    startMonitoring,
    stopMonitoring,
    refresh,
  };
};

export default useMonitoring;

