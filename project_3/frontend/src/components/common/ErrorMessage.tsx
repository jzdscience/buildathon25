import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
  className?: string;
  variant?: 'error' | 'warning';
  showIcon?: boolean;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  message, 
  onDismiss, 
  className = '',
  variant = 'error',
  showIcon = true
}) => {
  const variantClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800'
  };

  const iconColor = {
    error: 'text-red-500',
    warning: 'text-yellow-500'
  };

  return (
    <div className={`rounded-md border p-4 ${variantClasses[variant]} ${className}`}>
      <div className="flex items-start">
        {showIcon && (
          <AlertTriangle className={`mt-0.5 mr-3 h-5 w-5 flex-shrink-0 ${iconColor[variant]}`} />
        )}
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`ml-3 -mr-1 -mt-1 p-1.5 rounded-md hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              variant === 'error' 
                ? 'hover:bg-red-500 focus:ring-red-500' 
                : 'hover:bg-yellow-500 focus:ring-yellow-500'
            }`}
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;

