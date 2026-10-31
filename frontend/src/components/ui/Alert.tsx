import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';

interface AlertProps {
  type?: 'error' | 'warning' | 'info' | 'success';
  title?: string;
  message: string;
  code?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'error',
  title,
  message,
  code,
  onRetry,
  onDismiss,
  className = '',
}) => {
  const styles = {
    error: {
      bg: 'bg-red-950/40',
      border: 'border-red-800/60',
      text: 'text-red-300',
      titleColor: 'text-red-200',
      icon: <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" aria-hidden="true" />,
    },
    warning: {
      bg: 'bg-amber-950/40',
      border: 'border-amber-800/60',
      text: 'text-amber-300',
      titleColor: 'text-amber-200',
      icon: <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />,
    },
    info: {
      bg: 'bg-blue-950/40',
      border: 'border-blue-800/60',
      text: 'text-blue-300',
      titleColor: 'text-blue-200',
      icon: <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" aria-hidden="true" />,
    },
    success: {
      bg: 'bg-emerald-950/40',
      border: 'border-emerald-800/60',
      text: 'text-emerald-300',
      titleColor: 'text-emerald-200',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />,
    },
  }[type];

  return (
    <div
      role="alert"
      className={`rounded-lg p-4 border ${styles.bg} ${styles.border} ${className}`}
    >
      <div className="flex items-start gap-3">
        {styles.icon}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            {title && <h4 className={`text-sm font-semibold ${styles.titleColor}`}>{title}</h4>}
            {code && (
              <span className="font-mono text-xs px-1.5 py-0.5 rounded bg-black/40 text-slate-400 border border-slate-700/50">
                {code}
              </span>
            )}
          </div>
          <p className={`text-sm mt-1 leading-relaxed ${styles.text}`}>{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-xs font-medium px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-slate-400 hover:text-slate-200 p-1 rounded transition-colors"
            aria-label="Dismiss alert"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
