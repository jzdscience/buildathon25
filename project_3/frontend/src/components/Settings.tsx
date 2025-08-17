import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Wifi, WifiOff, Play, Square, Save, RotateCcw } from 'lucide-react';
import { useMonitoring } from '../hooks';
import { apiClient } from '../services/api';
import { Card, Button, LoadingSpinner, ErrorMessage, Badge } from './common';
import { Configuration, SlackConnectionTest } from '../types';

const Settings: React.FC = () => {
  const { status, loading: monitoringLoading, startMonitoring, stopMonitoring } = useMonitoring();
  const [config, setConfig] = useState<Configuration | null>(null);
  const [configLoading, setConfigLoading] = useState(true);
  const [configError, setConfigError] = useState<string | null>(null);
  const [slackTest, setSlackTest] = useState<SlackConnectionTest | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    loadConfiguration();
    testSlackConnection();
  }, []);

  const loadConfiguration = async () => {
    try {
      setConfigLoading(true);
      const response = await apiClient.config.getConfiguration();
      if (response.success && response.data) {
        setConfig(response.data);
      } else {
        setConfigError(response.error || 'Failed to load configuration');
      }
    } catch (err) {
      setConfigError('Failed to load configuration');
    } finally {
      setConfigLoading(false);
    }
  };

  const testSlackConnection = async () => {
    try {
      setTestingConnection(true);
      const response = await apiClient.slack.testConnection();
      if (response.success && response.data) {
        setSlackTest(response.data);
      }
    } catch (err) {
      console.error('Failed to test Slack connection:', err);
    } finally {
      setTestingConnection(false);
    }
  };

  const handleMonitoringToggle = async () => {
    try {
      if (status?.is_monitoring) {
        await stopMonitoring();
      } else {
        await startMonitoring();
      }
    } catch (err) {
      window.alert(`Failed to ${status?.is_monitoring ? 'stop' : 'start'} monitoring: ${err}`);
    }
  };

  const triggerAnalytics = async () => {
    try {
      await apiClient.bulk.generateAllAnalytics();
      window.alert('Analytics generation started in the background');
    } catch (err) {
      window.alert('Failed to trigger analytics generation');
    }
  };

  const syncChannels = async () => {
    try {
      await apiClient.bulk.syncAllChannels();
      window.alert('Channel sync started in the background');
    } catch (err) {
      window.alert('Failed to sync channels');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600">Configure system settings and monitoring preferences</p>
      </div>

      {/* Monitoring Controls */}
      <Card title="Monitoring Controls" subtitle="Start, stop, and manage sentiment monitoring">
        <div className="space-y-6">
          {/* Status display */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-3 ${
                status?.is_monitoring ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`} />
              <div>
                <div className="font-medium text-gray-900">
                  Monitoring Status
                </div>
                <div className="text-sm text-gray-600">
                  {status?.is_monitoring ? 'Active - Real-time analysis running' : 'Inactive - Not monitoring channels'}
                </div>
              </div>
            </div>
            
            <Badge variant={status?.is_monitoring ? 'success' : 'danger'}>
              {status?.is_monitoring ? 'Active' : 'Inactive'}
            </Badge>
          </div>

          {/* Controls */}
          <div className="flex flex-wrap gap-4">
            <Button
              onClick={handleMonitoringToggle}
              variant={status?.is_monitoring ? 'danger' : 'success'}
              leftIcon={status?.is_monitoring ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              loading={monitoringLoading}
            >
              {status?.is_monitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </Button>

            <Button
              onClick={triggerAnalytics}
              variant="outline"
              leftIcon={<SettingsIcon className="w-4 h-4" />}
            >
              Generate Analytics
            </Button>

            <Button
              onClick={syncChannels}
              variant="outline"
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              Sync All Channels
            </Button>
          </div>

          <div className="text-xs text-gray-500 p-3 bg-blue-50 rounded-lg">
            <strong>Note:</strong> Analytics are generated automatically every hour. Manual generation is useful for immediate updates or testing.
          </div>
        </div>
      </Card>

      {/* Slack Connection */}
      <Card title="Slack Integration" subtitle="Connection status and configuration">
        <div className="space-y-4">
          {testingConnection ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner message="Testing connection..." />
            </div>
          ) : slackTest ? (
            <div className="space-y-4">
              {/* Connection status */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  {slackTest.success ? (
                    <Wifi className="w-6 h-6 text-green-500 mr-3" />
                  ) : (
                    <WifiOff className="w-6 h-6 text-red-500 mr-3" />
                  )}
                  <div>
                    <div className="font-medium text-gray-900">
                      {slackTest.success ? 'Connected to Slack' : 'Connection Failed'}
                    </div>
                    <div className="text-sm text-gray-600">
                      {slackTest.success 
                        ? `Connected as ${slackTest.user} in ${slackTest.team}`
                        : slackTest.error || 'Unknown error'
                      }
                    </div>
                  </div>
                </div>
                
                <Badge variant={slackTest.success ? 'success' : 'danger'}>
                  {slackTest.success ? 'Connected' : 'Failed'}
                </Badge>
              </div>

              {/* Test again button */}
              <Button
                onClick={testSlackConnection}
                variant="outline"
                size="sm"
                leftIcon={<RotateCcw className="w-4 h-4" />}
              >
                Test Connection Again
              </Button>
            </div>
          ) : (
            <div className="text-center py-8">
              <WifiOff className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">Unable to test Slack connection</p>
            </div>
          )}
        </div>
      </Card>

      {/* Configuration */}
      <Card title="System Configuration" subtitle="Current system settings and thresholds">
        {configLoading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner message="Loading configuration..." />
          </div>
        ) : configError ? (
          <ErrorMessage message={configError} />
        ) : config ? (
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-4">Analysis Settings</h4>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Update Interval</span>
                    <span className="text-sm font-medium">{config.sentiment_update_interval_minutes} minutes</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Burnout Threshold</span>
                    <span className="text-sm font-medium">{config.burnout_threshold}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">Warning Threshold</span>
                    <span className="text-sm font-medium">{config.warning_threshold}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-4">API Configuration</h4>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">API Host</span>
                    <span className="text-sm font-medium">{config.api_host}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-sm text-gray-600">API Port</span>
                    <span className="text-sm font-medium">{config.api_port}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-xs text-gray-500 p-3 bg-yellow-50 rounded-lg">
              <strong>Note:</strong> Configuration changes require server restart and are managed through environment variables.
            </div>
          </div>
        ) : null}
      </Card>

      {/* System Information */}
      <Card title="System Information" subtitle="Application status and metadata">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Application</h4>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Version</span>
                <span className="text-sm font-medium">1.0.0</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Environment</span>
                <span className="text-sm font-medium">
                  {process.env.NODE_ENV || 'development'}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Build Date</span>
                <span className="text-sm font-medium">
                  {new Date().toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Features</h4>
            <div className="space-y-2">
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Real-time sentiment analysis
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Emoji sentiment detection
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Burnout risk assessment
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Team engagement metrics
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Actionable recommendations
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
