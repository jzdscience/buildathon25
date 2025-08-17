// API Response Types
export interface Channel {
  channel_id: string;
  channel_name: string;
  is_active: boolean;
  created_at: string;
}

export interface SummaryData {
  total_messages: number;
  active_users: number;
  avg_sentiment: number;
  avg_engagement: number;
  sentiment_category: SentimentCategory;
}

export interface TrendData {
  date: string;
  sentiment: number;
  messages: number;
  engagement: number;
}

export interface ChannelData {
  channel_id: string;
  channel_name: string;
  avg_sentiment: number;
  total_messages: number;
  avg_engagement: number;
  sentiment_category: SentimentCategory;
}

export interface InsightsData {
  overall_sentiment: number;
  sentiment_trend: TrendType;
  engagement_level: EngagementLevel;
  burnout_risk_score: number;
  week_start: string;
  week_end: string;
}

export interface BurnoutAlert {
  type: 'burnout_risk' | 'low_sentiment';
  severity: 'high' | 'medium' | 'low';
  message: string;
  user_id?: string;
}

export interface DashboardData {
  summary: SummaryData;
  trends: TrendData[];
  channels: ChannelData[];
  insights: InsightsData;
  burnout_alerts: BurnoutAlert[];
  recommendations: string[];
}

export interface SlackConnectionTest {
  success: boolean;
  user?: string;
  team?: string;
  error?: string;
}

export interface MonitoringStatus {
  is_monitoring: boolean;
  status: 'active' | 'stopped';
  timestamp: string;
}

export interface Statsummary {
  monitored_channels: number;
  monitoring_active: boolean;
  last_updated: string;
  system_status: string;
}

export interface Configuration {
  sentiment_update_interval_minutes: number;
  burnout_threshold: number;
  warning_threshold: number;
  api_host: string;
  api_port: number;
}

// Enum Types
export type SentimentCategory = 
  | 'very_positive' 
  | 'positive' 
  | 'neutral' 
  | 'negative' 
  | 'very_negative';

export type TrendType = 'improving' | 'declining' | 'stable';

export type EngagementLevel = 'high' | 'medium' | 'low';

export type AlertSeverity = 'high' | 'medium' | 'low';

// Component Props Types
export interface DashboardProps {
  refreshInterval?: number;
}

export interface ChartProps {
  data: TrendData[];
  height?: number;
  className?: string;
}

export interface SentimentMeterProps {
  value: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export interface AlertBannerProps {
  alerts: BurnoutAlert[];
  onDismiss?: (index: number) => void;
}

export interface ChannelManagerProps {
  channels: Channel[];
  onAddChannel: (channelId: string) => void;
  onRemoveChannel: (channelId: string) => void;
  loading?: boolean;
}

export interface RecommendationListProps {
  recommendations: string[];
  className?: string;
}

// Utility Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

export interface LoadingState {
  loading: boolean;
  error?: string;
}

export interface TimeRange {
  days: number;
  label: string;
}

// Chart Data Types
export interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
}

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
}

export interface EngagementMetrics {
  messages_per_day: number;
  reactions_per_message: number;
  thread_participation: number;
  response_rate: number;
}

// Form Types
export interface AddChannelForm {
  channel_id: string;
}

export interface ConfigForm {
  sentiment_update_interval_minutes: number;
  burnout_threshold: number;
  warning_threshold: number;
}

// Hook Return Types
export interface UseDashboardReturn {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export interface UseChannelsReturn {
  channels: Channel[];
  loading: boolean;
  error: string | null;
  addChannel: (channelId: string) => Promise<void>;
  removeChannel: (channelId: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export interface UseMonitoringReturn {
  status: MonitoringStatus | null;
  loading: boolean;
  error: string | null;
  startMonitoring: () => Promise<void>;
  stopMonitoring: () => Promise<void>;
  refresh: () => Promise<void>;
}

// Theme Types
export interface ThemeColors {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  danger: string;
  neutral: string;
}

export interface Theme {
  colors: ThemeColors;
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
}

// Export all types as default for easy importing
export default interface Types {
  Channel: Channel;
  DashboardData: DashboardData;
  SentimentCategory: SentimentCategory;
  TrendType: TrendType;
  EngagementLevel: EngagementLevel;
  BurnoutAlert: BurnoutAlert;
}

