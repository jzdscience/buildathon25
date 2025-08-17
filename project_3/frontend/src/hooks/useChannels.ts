import { useState, useEffect, useCallback } from 'react';
import { Channel, UseChannelsReturn } from '../types';
import { apiClient, formatApiError } from '../services/api';

const useChannels = (): UseChannelsReturn => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.channels.getChannels();
      
      if (response.success && response.data) {
        setChannels(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const addChannel = useCallback(async (channelId: string) => {
    try {
      setError(null);
      
      const response = await apiClient.channels.addChannel(channelId);
      
      if (response.success && response.data) {
        setChannels(prev => [...prev, response.data!]);
      } else if (response.error) {
        setError(response.error);
        throw new Error(response.error);
      }
    } catch (err) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const removeChannel = useCallback(async (channelId: string) => {
    try {
      setError(null);
      
      const response = await apiClient.channels.removeChannel(channelId);
      
      if (response.success) {
        setChannels(prev => prev.filter(channel => channel.channel_id !== channelId));
      } else if (response.error) {
        setError(response.error);
        throw new Error(response.error);
      }
    } catch (err) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  // Initial load
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    channels,
    loading,
    error,
    addChannel,
    removeChannel,
    refresh,
  };
};

export default useChannels;

