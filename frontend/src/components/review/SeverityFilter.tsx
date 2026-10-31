import React from 'react';
import { Search, Filter, X } from 'lucide-react';
import type { Category, FindingCounts, Severity } from '../../types/review';

interface SeverityFilterProps {
  counts: FindingCounts;
  total: number;
  activeSeverity: Severity | 'all';
  activeCategory: Category | 'all';
  searchQuery: string;
  onSelectSeverity: (severity: Severity | 'all') => void;
  onSelectCategory: (category: Category | 'all') => void;
  onSearchChange: (query: string) => void;
  className?: string;
}

export const SeverityFilter: React.FC<SeverityFilterProps> = ({
  counts,
  total,
  activeSeverity,
  activeCategory,
  searchQuery,
  onSelectSeverity,
  onSelectCategory,
  onSearchChange,
  className = '',
}) => {
  const severities: Array<{ id: Severity | 'all'; label: string; count: number; color: string }> = [
    { id: 'all', label: 'All', count: total, color: 'text-slate-200' },
    { id: 'critical', label: 'Critical', count: counts.critical, color: 'text-red-400' },
    { id: 'high', label: 'High', count: counts.high, color: 'text-orange-400' },
    { id: 'medium', label: 'Medium', count: counts.medium, color: 'text-amber-400' },
    { id: 'low', label: 'Low', count: counts.low, color: 'text-blue-400' },
    { id: 'info', label: 'Info', count: counts.info, color: 'text-slate-400' },
  ];

  const categories: Array<{ id: Category | 'all'; label: string }> = [
    { id: 'all', label: 'All Categories' },
    { id: 'security', label: 'Security' },
    { id: 'correctness', label: 'Correctness' },
    { id: 'performance', label: 'Performance' },
    { id: 'maintainability', label: 'Maintainability' },
    { id: 'style', label: 'Style' },
    { id: 'documentation', label: 'Documentation' },
  ];

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Top Filter Bar: Severities + Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Severity Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 text-xs no-scrollbar">
          {severities.map((item) => {
            const isSelected = activeSeverity === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectSeverity(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all shrink-0 ${
                  isSelected
                    ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
                }`}
                aria-pressed={isSelected}
              >
                <span>{item.label}</span>
                <span
                  className={`px-1.5 py-0.2 rounded-full font-mono text-[10px] ${
                    isSelected ? 'bg-slate-700 text-white' : 'bg-slate-800/80 text-slate-400'
                  }`}
                >
                  {item.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search input */}
        <div className="relative w-full sm:w-64 shrink-0">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Filter findings..."
            className="w-full pl-8 pr-8 py-1.5 text-xs bg-background-surface border border-border-subtle rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/80 transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
              aria-label="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Category Dropdown and Active Filter pills */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <select
            value={activeCategory}
            onChange={(e) => onSelectCategory(e.target.value as Category | 'all')}
            className="bg-background-surface border border-border-subtle rounded-md px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-indigo-500/80"
            aria-label="Filter by category"
          >
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        {(activeSeverity !== 'all' || activeCategory !== 'all' || searchQuery) && (
          <button
            onClick={() => {
              onSelectSeverity('all');
              onSelectCategory('all');
              onSearchChange('');
            }}
            className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium"
          >
            Reset Filters
          </button>
        )}
      </div>
    </div>
  );
};
