import React, { useState } from 'react';
import { RefreshCw, Calendar, TrendingUp, Users, MessageSquare, AlertTriangle } from 'lucide-react';
import { useDashboard } from '../hooks';
import { 
  LoadingSpinner, 
  ErrorMessage, 
  Card, 
  Button, 
  Badge, 
  SentimentMeter,
  AlertBanner 
} from './common';
import SentimentChart from './charts/SentimentChart';
import EngagementChart from './charts/EngagementChart';
import ChannelOverview from './ChannelOverview';
import RecommendationsList from './RecommendationsList';
import { TimeRange } from '../types';

const Dashboard: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>({ days: 7, label: '7 days' });
  const [dismissedAlerts, setDismissedAlerts] = useState<number[]>([]);
  
  const { data, loading, error, refresh } = useDashboard(
    selectedTimeRange.days, 
    true, // auto refresh
    60000 // 1 minute interval
  );

  const timeRanges: TimeRange[] = [
    { days: 1, label: 'Today' },
    { days: 7, label: '7 days' },
    { days: 14, label: '14 days' },
    { days: 30, label: '30 days' }
  ];

  const handleDismissAlert = (index: number) => {
    setDismissedAlerts(prev => [...prev, index]);
  };

  const filteredAlerts = data?.burnout_alerts?.filter((_, index) => 
    !dismissedAlerts.includes(index)
  ) || [];

  const getSentimentTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'declining':
        return <TrendingUp className="w-4 h-4 text-red-600 transform rotate-180" />;
      default:
        return <TrendingUp className="w-4 h-4 text-gray-400" />;
    }
  };

  const getEngagementColor = (level: string) => {
    switch (level) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'danger';
      default: return 'default';
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" message="Loading dashboard..." />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="max-w-md mx-auto mt-8">
        <ErrorMessage 
          message={error} 
          onDismiss={() => window.location.reload()} 
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Team Pulse Dashboard</h2>
          <p className="text-gray-600">Real-time insights into team engagement and sentiment</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Time range selector */}
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            {timeRanges.map((range) => (
              <button
                key={range.days}
                onClick={() => setSelectedTimeRange(range)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  selectedTimeRange.days === range.days
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                } border-r border-gray-300 last:border-r-0`}
              >
                {range.label}
              </button>
            ))}
          </div>
          
          <Button
            onClick={refresh}
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Alert banners */}
      {filteredAlerts.length > 0 && (
        <AlertBanner alerts={filteredAlerts} onDismiss={handleDismissAlert} />
      )}

      {/* Summary cards */}
      {data?.summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-lg">
              <MessageSquare className="w-6 h-6 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{data.summary.total_messages}</div>
            <div className="text-sm text-gray-600">Total Messages</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-green-100 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{data.summary.active_users}</div>
            <div className="text-sm text-gray-600">Active Users</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {(data.summary.avg_engagement * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Engagement Rate</div>
          </Card>

          <Card className="text-center">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{filteredAlerts.length}</div>
            <div className="text-sm text-gray-600">Active Alerts</div>
          </Card>
        </div>
      )}

      {/* Sentiment and insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall sentiment */}
        <Card title="Team Sentiment" subtitle="Current overall mood">
          {data?.summary && (
            <div className="flex items-center justify-center">
              <SentimentMeter 
                value={data.summary.avg_sentiment} 
                size="lg"
                showLabel={true}
              />
            </div>
          )}
        </Card>

        {/* Key insights */}
        <Card title="Weekly Insights" subtitle="Key trends and patterns">
          {data?.insights && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Sentiment Trend</span>
                <div className="flex items-center">
                  {getSentimentTrendIcon(data.insights.sentiment_trend)}
                  <span className="ml-2 text-sm font-medium capitalize">
                    {data.insights.sentiment_trend}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Engagement Level</span>
                <Badge variant={getEngagementColor(data.insights.engagement_level) as any}>
                  {data.insights.engagement_level ? data.insights.engagement_level.toUpperCase() : 'N/A'}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Burnout Risk</span>
                <span className={`text-sm font-medium ${
                  data.insights.burnout_risk_score > 0.7 ? 'text-red-600' :
                  data.insights.burnout_risk_score > 0.4 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {(data.insights.burnout_risk_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          )}
        </Card>

        {/* Time period info */}
        <Card title="Analysis Period" subtitle="Current data scope">
          <div className="space-y-4">
            <div className="flex items-center">
              <Calendar className="w-5 h-5 text-gray-400 mr-3" />
              <div>
                <div className="text-sm font-medium">{selectedTimeRange.label}</div>
                <div className="text-xs text-gray-500">
                  {data?.insights?.week_start && new Date(data.insights.week_start).toLocaleDateString()}
                  {' - '}
                  {data?.insights?.week_end && new Date(data.insights.week_end).toLocaleDateString()}
                </div>
              </div>
            </div>
            
            <div className="text-sm text-gray-600">
              <div>Last updated: {new Date().toLocaleTimeString()}</div>
              <div className="text-xs text-gray-500 mt-1">
                Auto-refreshes every minute
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card title="Sentiment Trends" subtitle="Daily sentiment patterns">
          {data?.trends && <SentimentChart data={data.trends} />}
        </Card>

        <Card title="Engagement Metrics" subtitle="Team participation levels">
          {data?.trends && <EngagementChart data={data.trends} />}
        </Card>
      </div>

      {/* Channel overview and recommendations */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card title="Channel Overview" subtitle="Performance by channel">
          {data?.channels && <ChannelOverview channels={data.channels} />}
        </Card>

        <Card title="Recommendations" subtitle="Actionable insights for managers">
          {data?.recommendations && <RecommendationsList recommendations={data.recommendations} />}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
