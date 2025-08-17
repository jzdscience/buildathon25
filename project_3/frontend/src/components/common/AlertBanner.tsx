import React from 'react';
import { AlertTriangle, X, AlertCircle, Info } from 'lucide-react';
import { AlertBannerProps, BurnoutAlert } from '../../types';

const AlertBanner: React.FC<AlertBannerProps> = ({ alerts, onDismiss }) => {
  if (!alerts || alerts.length === 0) return null;

  const getAlertIcon = (type: BurnoutAlert['type']) => {
    switch (type) {
      case 'burnout_risk':
        return AlertTriangle;
      case 'low_sentiment':
        return AlertCircle;
      default:
        return Info;
    }
  };

  const getAlertStyles = (severity: BurnoutAlert['severity']) => {
    switch (severity) {
      case 'high':
        return {
          container: 'bg-red-50 border-red-200',
          text: 'text-red-800',
          icon: 'text-red-500',
          button: 'text-red-600 hover:bg-red-100'
        };
      case 'medium':
        return {
          container: 'bg-yellow-50 border-yellow-200',
          text: 'text-yellow-800',
          icon: 'text-yellow-500',
          button: 'text-yellow-600 hover:bg-yellow-100'
        };
      case 'low':
        return {
          container: 'bg-blue-50 border-blue-200',
          text: 'text-blue-800',
          icon: 'text-blue-500',
          button: 'text-blue-600 hover:bg-blue-100'
        };
    }
  };

  return (
    <div className="space-y-3">
      {alerts.map((alert, index) => {
        const Icon = getAlertIcon(alert.type);
        const styles = getAlertStyles(alert.severity);
        
        return (
          <div
            key={`${alert.type}-${index}`}
            className={`rounded-md border p-4 ${styles.container}`}
          >
            <div className="flex items-start">
              <Icon className={`mt-0.5 mr-3 h-5 w-5 flex-shrink-0 ${styles.icon}`} />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className={`text-sm font-medium ${styles.text}`}>
                      {alert.severity === 'high' ? 'High Priority Alert' : 
                       alert.severity === 'medium' ? 'Alert' : 'Notice'}
                    </h3>
                    <p className={`mt-1 text-sm ${styles.text}`}>
                      {alert.message}
                    </p>
                  </div>
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(index)}
                      className={`ml-4 -mr-1 -mt-1 p-1.5 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 ${styles.button}`}
                      aria-label="Dismiss alert"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
                {alert.user_id && (
                  <div className={`mt-2 text-xs ${styles.text} opacity-75`}>
                    User ID: {alert.user_id.substring(0, 8)}...
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AlertBanner;

