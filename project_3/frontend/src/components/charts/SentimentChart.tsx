import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { TrendData } from '../../types';

interface SentimentChartProps {
  data: TrendData[];
  height?: number;
}

const SentimentChart: React.FC<SentimentChartProps> = ({ data, height = 300 }) => {
  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'MMM dd');
    } catch {
      return dateString;
    }
  };

  const formatSentiment = (value: number) => {
    return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(1)}%`;
  };

  const getSentimentColor = (value: number) => {
    if (value >= 0.3) return '#22c55e'; // green
    if (value >= 0.1) return '#84cc16'; // light green
    if (value >= -0.1) return '#6b7280'; // gray
    if (value >= -0.3) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">
            {formatDate(label)}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Sentiment: <span className="font-medium" style={{ color: getSentimentColor(data.sentiment) }}>
              {formatSentiment(data.sentiment)}
            </span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {data.messages} messages
          </p>
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <div className="text-lg font-medium">No sentiment data available</div>
          <div className="text-sm">Data will appear here once messages are analyzed</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            domain={[-1, 1]}
            tickFormatter={formatSentiment}
            stroke="#6b7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="sentiment" 
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ r: 6, fill: '#3b82f6', strokeWidth: 2, stroke: '#ffffff' }}
            activeDot={{ r: 8, fill: '#3b82f6' }}
          />
          {/* Zero line */}
          <Line 
            type="monotone" 
            dataKey={() => 0} 
            stroke="#d1d5db"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            activeDot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SentimentChart;

