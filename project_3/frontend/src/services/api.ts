import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  Channel,
  DashboardData,
  SlackConnectionTest,
  MonitoringStatus,
  Statsummary,
  Configuration,
  ApiResponse
} from '../types';

// Define error response interface
interface ErrorResponse {
  error?: string;
  detail?: string;
  message?: string;
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    const method = config.method ? config.method.toUpperCase() : 'UNKNOWN';
    const url = config.url || 'unknown-url';
    console.log(`Making ${method} request to ${url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response?.status === 401) {
      // Handle authentication errors if needed
      console.warn('Authentication required');
    } else if (error.response?.status === 500) {
      console.error('Server error occurred');
    }
    
    return Promise.reject(error);
  }
);

// Utility function to handle API responses
const handleResponse = <T>(promise: Promise<AxiosResponse<T>>): Promise<ApiResponse<T>> => {
  return promise
    .then((response) => ({
      data: response.data,
      success: true,
    }))
    .catch((error: AxiosError) => {
      const errorData = error.response?.data as ErrorResponse;
      return {
        error: errorData?.error || errorData?.detail || errorData?.message || error.message,
        success: false,
      };
    });
};

// Health and Status APIs
export const healthApi = {
  check: () => handleResponse(api.get('/health')),
  
  getStatus: () => handleResponse(api.get('/status')),
};

// Slack APIs
export const slackApi = {
  testConnection: (): Promise<ApiResponse<SlackConnectionTest>> =>
    handleResponse(api.get<SlackConnectionTest>('/slack/test')),
};

// Channel Management APIs
export const channelApi = {
  getChannels: (): Promise<ApiResponse<Channel[]>> =>
    handleResponse(api.get<Channel[]>('/channels')),
    
  addChannel: (channelId: string): Promise<ApiResponse<Channel>> =>
    handleResponse(api.post<Channel>('/channels', { channel_id: channelId })),
    
  removeChannel: (channelId: string): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.delete(`/channels/${channelId}`)),
};

// Dashboard APIs
export const dashboardApi = {
  getDashboardData: (days: number = 7): Promise<ApiResponse<DashboardData>> =>
    handleResponse(api.get<DashboardData>(`/dashboard?days=${days}`)),
    
  exportData: (days: number = 7, format: string = 'json'): Promise<ApiResponse<any>> =>
    handleResponse(api.get(`/export/dashboard-data?days=${days}&format=${format}`)),
};

// Analytics APIs
export const analyticsApi = {
  generateDailyStats: (targetDate?: string): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/analytics/daily-stats', { target_date: targetDate })),
    
  generateWeeklyInsights: (weekStart?: string): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/analytics/weekly-insights', { week_start: weekStart })),
    
  getSentimentTrends: (days: number = 7, channelId?: string): Promise<ApiResponse<any>> =>
    handleResponse(api.get(`/sentiment/trends?days=${days}${channelId ? `&channel_id=${channelId}` : ''}`)),
};

// Monitoring APIs
export const monitoringApi = {
  getStatus: (): Promise<ApiResponse<MonitoringStatus>> =>
    handleResponse(api.get<MonitoringStatus>('/monitoring/status')),
    
  startMonitoring: (): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/monitoring/start')),
    
  stopMonitoring: (): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/monitoring/stop')),
};

// Configuration APIs
export const configApi = {
  getConfiguration: (): Promise<ApiResponse<Configuration>> =>
    handleResponse(api.get<Configuration>('/config')),
};

// Bulk Operations APIs
export const bulkApi = {
  syncAllChannels: (): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/bulk/sync-channels')),
    
  generateAllAnalytics: (): Promise<ApiResponse<{ message: string }>> =>
    handleResponse(api.post('/bulk/generate-analytics')),
};

// Statistics APIs
export const statsApi = {
  getSummary: (): Promise<ApiResponse<Statsummary>> =>
    handleResponse(api.get<Statsummary>('/stats/summary')),
};

// Combined API object for easy importing
export const apiClient = {
  health: healthApi,
  slack: slackApi,
  channels: channelApi,
  dashboard: dashboardApi,
  analytics: analyticsApi,
  monitoring: monitoringApi,
  config: configApi,
  bulk: bulkApi,
  stats: statsApi,
};

// Utility functions
export const formatApiError = (error: any): string => {
  if (typeof error === 'string') return error;
  if (error?.response?.data?.error) return error.response.data.error;
  if (error?.message) return error.message;
  return 'An unexpected error occurred';
};

export const isApiError = (response: ApiResponse<any>): response is { error: string; success: false } => {
  return !response.success && !!response.error;
};

// Polling utility for real-time updates
export class ApiPoller {
  private intervalId: number | null = null;
  private isPolling = false;
  
  start<T>(
    apiCall: () => Promise<ApiResponse<T>>,
    callback: (data: T) => void,
    errorCallback: (error: string) => void,
    interval: number = 30000 // 30 seconds default
  ) {
    if (this.isPolling) {
      this.stop();
    }
    
    this.isPolling = true;
    
    // Initial call
    apiCall().then(response => {
      if (response.success && response.data) {
        callback(response.data);
      } else if (response.error) {
        errorCallback(response.error);
      }
    });
    
    // Set up polling
    this.intervalId = window.setInterval(async () => {
      try {
        const response = await apiCall();
        if (response.success && response.data) {
          callback(response.data);
        } else if (response.error) {
          errorCallback(response.error);
        }
      } catch (error) {
        errorCallback(formatApiError(error));
      }
    }, interval);
  }
  
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isPolling = false;
  }
  
  get isActive() {
    return this.isPolling;
  }
}

// Export default api client
export default apiClient;
