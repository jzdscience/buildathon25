import React from 'react';
import { CheckCircle2, Lightbulb, AlertTriangle, TrendingUp } from 'lucide-react';
import { RecommendationListProps } from '../types';

const RecommendationsList: React.FC<RecommendationListProps> = ({ 
  recommendations, 
  className = '' 
}) => {
  const getRecommendationIcon = (recommendation: string) => {
    const text = recommendation.toLowerCase();
    
    if (text.includes('burnout') || text.includes('risk') || text.includes('stress')) {
      return <AlertTriangle className="w-5 h-5 text-orange-500" />;
    } else if (text.includes('great') || text.includes('excellent') || text.includes('continue')) {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    } else if (text.includes('improve') || text.includes('increase') || text.includes('enhance')) {
      return <TrendingUp className="w-5 h-5 text-blue-500" />;
    } else {
      return <Lightbulb className="w-5 h-5 text-purple-500" />;
    }
  };

  const getRecommendationPriority = (recommendation: string) => {
    const text = recommendation.toLowerCase();
    
    if (text.includes('burnout') || text.includes('concerning') || text.includes('risk')) {
      return 'high';
    } else if (text.includes('consider') || text.includes('review') || text.includes('low')) {
      return 'medium';
    } else {
      return 'low';
    }
  };

  const getPriorityStyles = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-400 bg-red-50';
      case 'medium':
        return 'border-l-yellow-400 bg-yellow-50';
      case 'low':
        return 'border-l-blue-400 bg-blue-50';
      default:
        return 'border-l-gray-400 bg-gray-50';
    }
  };

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className={`flex items-center justify-center h-48 text-gray-500 ${className}`}>
        <div className="text-center">
          <Lightbulb className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <div className="text-lg font-medium">No recommendations available</div>
          <div className="text-sm">Insights will appear here as data is analyzed</div>
        </div>
      </div>
    );
  }

  // Sort recommendations by priority
  const sortedRecommendations = [...recommendations].sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const aPriority = getRecommendationPriority(a);
    const bPriority = getRecommendationPriority(b);
    return priorityOrder[bPriority as keyof typeof priorityOrder] - priorityOrder[aPriority as keyof typeof priorityOrder];
  });

  return (
    <div className={`space-y-3 ${className}`}>
      {sortedRecommendations.map((recommendation, index) => {
        const priority = getRecommendationPriority(recommendation);
        const icon = getRecommendationIcon(recommendation);
        const styles = getPriorityStyles(priority);
        
        return (
          <div
            key={index}
            className={`border-l-4 p-4 rounded-r-lg ${styles} transition-all duration-200 hover:shadow-sm`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                {icon}
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-800 leading-relaxed">
                  {recommendation}
                </p>
                {priority === 'high' && (
                  <div className="mt-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      High Priority
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
      
      {/* Summary footer */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Total Recommendations</span>
          <span className="font-semibold text-gray-900">{recommendations.length}</span>
        </div>
        
        {(() => {
          const priorityCounts = recommendations.reduce((acc, rec) => {
            const priority = getRecommendationPriority(rec);
            acc[priority] = (acc[priority] || 0) + 1;
            return acc;
          }, {} as Record<string, number>);
          
          return (
            <div className="mt-2 flex items-center space-x-4 text-xs">
              {priorityCounts.high && (
                <div className="flex items-center text-red-600">
                  <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
                  {priorityCounts.high} High Priority
                </div>
              )}
              {priorityCounts.medium && (
                <div className="flex items-center text-yellow-600">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                  {priorityCounts.medium} Medium Priority
                </div>
              )}
              {priorityCounts.low && (
                <div className="flex items-center text-blue-600">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
                  {priorityCounts.low} Low Priority
                </div>
              )}
            </div>
          );
        })()}
      </div>
    </div>
  );
};

export default RecommendationsList;

