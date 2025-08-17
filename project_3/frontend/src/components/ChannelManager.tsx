import React, { useState } from 'react';
import { Plus, Trash2, Hash, Calendar, RotateCcw, AlertCircle } from 'lucide-react';
import { useChannels } from '../hooks';
import { Card, Button, LoadingSpinner, ErrorMessage } from './common';

const ChannelManager: React.FC = () => {
  const { channels, loading, error, addChannel, removeChannel, refresh } = useChannels();
  const [newChannelId, setNewChannelId] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const [removingChannels, setRemovingChannels] = useState<Set<string>>(new Set());

  const handleAddChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newChannelId.trim()) {
      setAddError('Please enter a channel ID');
      return;
    }

    setIsAdding(true);
    setAddError(null);

    try {
      await addChannel(newChannelId.trim());
      setNewChannelId('');
    } catch (err) {
      setAddError(err instanceof Error ? err.message : 'Failed to add channel');
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemoveChannel = async (channelId: string) => {
    if (!window.confirm('Are you sure you want to remove this channel from monitoring?')) {
      return;
    }

    setRemovingChannels(prev => new Set(prev).add(channelId));

    try {
      await removeChannel(channelId);
    } catch (err) {
      window.alert(`Failed to remove channel: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setRemovingChannels(prev => {
        const newSet = new Set(prev);
        newSet.delete(channelId);
        return newSet;
      });
    }
  };

  const formatChannelName = (name: string) => {
    return name.startsWith('#') ? name : `#${name}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Channel Management</h2>
          <p className="text-gray-600">Configure which Slack channels to monitor for sentiment analysis</p>
        </div>
        
        <Button
          onClick={refresh}
          variant="outline"
          size="sm"
          leftIcon={<RotateCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      {/* Add Channel Form */}
      <Card title="Add New Channel" subtitle="Enter the Slack channel ID you want to monitor">
        <form onSubmit={handleAddChannel} className="space-y-4">
          <div>
            <label htmlFor="channelId" className="block text-sm font-medium text-gray-700 mb-2">
              Channel ID
            </label>
            <div className="flex space-x-3">
              <div className="flex-1">
                <input
                  type="text"
                  id="channelId"
                  value={newChannelId}
                  onChange={(e) => setNewChannelId(e.target.value)}
                  placeholder="C1234567890 or #channel-name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={isAdding}
                />
              </div>
              <Button
                type="submit"
                variant="primary"
                leftIcon={<Plus className="w-4 h-4" />}
                loading={isAdding}
                disabled={!newChannelId.trim()}
              >
                Add Channel
              </Button>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              You can find the channel ID in Slack by right-clicking on the channel name and selecting "Copy link". The ID is the part after the last slash.
            </p>
          </div>

          {addError && (
            <ErrorMessage message={addError} onDismiss={() => setAddError(null)} />
          )}
        </form>
      </Card>

      {/* Channel List */}
      <Card 
        title="Monitored Channels" 
        subtitle={`Currently monitoring ${channels.length} channel${channels.length !== 1 ? 's' : ''}`}
      >
        {loading && channels.length === 0 ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner message="Loading channels..." />
          </div>
        ) : error && channels.length === 0 ? (
          <ErrorMessage message={error} />
        ) : channels.length === 0 ? (
          <div className="text-center py-12">
            <Hash className="w-12 h-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No channels configured</h3>
            <p className="text-gray-500 mb-6">
              Add your first Slack channel above to start monitoring team sentiment.
            </p>
            <div className="text-sm text-gray-400 space-y-1">
              <p>💡 Tip: Start with general team channels like #general or #random</p>
              <p>📊 Data will be collected and analyzed automatically once channels are added</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {channels.map((channel) => (
              <div
                key={channel.channel_id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-primary-100 rounded-lg">
                    <Hash className="w-5 h-5 text-primary-600" />
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900">
                      {formatChannelName(channel.channel_name)}
                    </h4>
                    <p className="text-xs text-gray-500">
                      ID: {channel.channel_id}
                    </p>
                    <div className="flex items-center mt-1 text-xs text-gray-400">
                      <Calendar className="w-3 h-3 mr-1" />
                      Added {formatDate(channel.created_at)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Status indicator */}
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full ${
                      channel.is_active ? 'bg-green-500' : 'bg-gray-400'
                    }`} />
                    <span className="ml-2 text-xs text-gray-500">
                      {channel.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  {/* Remove button */}
                  <Button
                    onClick={() => handleRemoveChannel(channel.channel_id)}
                    variant="outline"
                    size="sm"
                    leftIcon={<Trash2 className="w-4 h-4" />}
                    loading={removingChannels.has(channel.channel_id)}
                    className="text-red-600 border-red-300 hover:bg-red-50"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Instructions */}
      <Card title="Setup Instructions" subtitle="How to configure your Slack channels">
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs mr-2">1</span>
                Find Channel ID
              </h4>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• Right-click on the channel name in Slack</li>
                <li>• Select "Copy link"</li>
                <li>• Extract the ID from the URL (e.g., C1234567890)</li>
                <li>• Or use the channel name with # prefix</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <span className="flex items-center justify-center w-6 h-6 bg-green-100 text-green-600 rounded-full text-xs mr-2">2</span>
                Recommended Channels
              </h4>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• #general - Overall team discussions</li>
                <li>• #random - Casual conversations</li>
                <li>• #standups - Daily team updates</li>
                <li>• Project-specific channels</li>
              </ul>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Important Notes:</p>
                <ul className="space-y-1">
                  <li>• The Slack bot must be added to channels before they can be monitored</li>
                  <li>• Historical messages (up to 7 days) will be analyzed when a channel is added</li>
                  <li>• Real-time analysis begins immediately after adding a channel</li>
                  <li>• Thread messages and reactions are included in sentiment analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChannelManager;
