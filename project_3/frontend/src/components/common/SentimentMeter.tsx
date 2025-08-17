import React from 'react';
import { SentimentMeterProps, SentimentCategory } from '../../types';

const SentimentMeter: React.FC<SentimentMeterProps> = ({ 
  value, 
  size = 'md', 
  showLabel = true, 
  className = '' 
}) => {
  // Safety check: ensure value is a valid number
  const safeValue = typeof value === 'number' && !isNaN(value) ? value : 0;

  const getSentimentCategory = (sentiment: number): SentimentCategory => {
    if (sentiment >= 0.6) return 'very_positive';
    if (sentiment >= 0.2) return 'positive';
    if (sentiment >= -0.2) return 'neutral';
    if (sentiment >= -0.6) return 'negative';
    return 'very_negative';
  };

  const getSentimentColor = (category: SentimentCategory): string => {
    switch (category) {
      case 'very_positive': return 'bg-green-500';
      case 'positive': return 'bg-green-400';
      case 'neutral': return 'bg-gray-400';
      case 'negative': return 'bg-orange-400';
      case 'very_negative': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const getSentimentLabel = (category: SentimentCategory): string => {
    switch (category) {
      case 'very_positive': return 'Very Positive';
      case 'positive': return 'Positive';
      case 'neutral': return 'Neutral';
      case 'negative': return 'Negative';
      case 'very_negative': return 'Very Negative';
      default: return 'Unknown';
    }
  };

  const sizeClasses = {
    sm: { container: 'w-16 h-16', text: 'text-xs' },
    md: { container: 'w-20 h-20', text: 'text-sm' },
    lg: { container: 'w-24 h-24', text: 'text-base' }
  };

  const category = getSentimentCategory(safeValue);
  const colorClass = getSentimentColor(category);
  const label = getSentimentLabel(category);
  
  // Convert sentiment value (-1 to 1) to percentage (0 to 100)
  const percentage = ((safeValue + 1) / 2) * 100;
  
  // Create the conic gradient for the circular progress
  const gradientStyle = {
    background: `conic-gradient(${colorClass.replace('bg-', '#')} ${percentage * 3.6}deg, #e5e7eb 0deg)`
  };

  // Check if we have valid data
  const hasValidData = typeof value === 'number' && !isNaN(value);

  return (
    <div className={`flex flex-col items-center space-y-2 ${className}`}>
      <div className={`relative ${sizeClasses[size].container} rounded-full`}>
        {/* Outer circle with gradient */}
        <div 
          className="absolute inset-0 rounded-full p-1"
          style={gradientStyle}
        >
          {/* Inner white circle */}
          <div className="w-full h-full bg-white rounded-full flex items-center justify-center">
            <div className="text-center">
              <div className={`font-bold text-gray-800 ${sizeClasses[size].text}`}>
                {hasValidData ? (
                  `${safeValue >= 0 ? '+' : ''}${(safeValue * 100).toFixed(0)}`
                ) : (
                  '--'
                )}
              </div>
              <div className={`text-gray-500 ${sizeClasses[size].text === 'text-base' ? 'text-xs' : 'text-xs'}`}>
                %
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {showLabel && (
        <div className="text-center">
          <div className={`font-medium text-gray-800 ${sizeClasses[size].text}`}>
            {hasValidData ? label : 'No Data'}
          </div>
          <div className={`text-gray-500 ${sizeClasses[size].text === 'text-base' ? 'text-xs' : 'text-xs'}`}>
            Score: {hasValidData ? safeValue.toFixed(2) : 'N/A'}
          </div>
        </div>
      )}
    </div>
  );
};

export default SentimentMeter;
