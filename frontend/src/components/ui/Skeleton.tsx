import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div
    className={`animate-pulse rounded bg-slate-800/60 border border-slate-700/30 ${className}`}
    aria-hidden="true"
  />
);

export const FindingCardSkeleton: React.FC = () => (
  <div className="rounded-lg p-5 bg-background-card border border-border-subtle space-y-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Skeleton className="w-16 h-5" />
        <Skeleton className="w-20 h-5" />
        <Skeleton className="w-14 h-5" />
      </div>
      <Skeleton className="w-24 h-5" />
    </div>
    <Skeleton className="w-3/4 h-6" />
    <Skeleton className="w-full h-12" />
    <Skeleton className="w-full h-24" />
  </div>
);

export const ReviewSummarySkeleton: React.FC = () => (
  <div className="rounded-xl p-6 bg-background-card border border-border-subtle space-y-4">
    <div className="flex items-center justify-between">
      <Skeleton className="w-48 h-7" />
      <div className="flex gap-2">
        <Skeleton className="w-16 h-6" />
        <Skeleton className="w-16 h-6" />
      </div>
    </div>
    <Skeleton className="w-full h-16" />
    <div className="grid grid-cols-5 gap-3 pt-2">
      {[...Array(5)].map((_, i) => (
        <Skeleton key={i} className="h-16 rounded-lg" />
      ))}
    </div>
  </div>
);
