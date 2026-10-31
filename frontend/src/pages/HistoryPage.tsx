import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  History,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Search,
  RefreshCw,
  Hash,
} from 'lucide-react';
import { apiClient, ApiError } from '../api/client';
import type { PaginatedResponse, ReviewSummary } from '../types/review';
import { Alert } from '../components/ui/Alert';
import { Skeleton } from '../components/ui/Skeleton';

export const HistoryPage: React.FC = () => {
  const [data, setData] = useState<PaginatedResponse<ReviewSummary> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ status: number; code: string; message: string } | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.getHistory(page, pageSize);
      setData(result);
    } catch (err) {
      if (err instanceof ApiError) {
        setError({
          status: err.status,
          code: err.code,
          message: err.detail,
        });
      } else {
        setError({
          status: 0,
          code: 'FETCH_ERROR',
          message: err instanceof Error ? err.message : 'Failed to retrieve review history from server.',
        });
      }
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const items = data?.items || [];
  const filteredItems = search.trim()
    ? items.filter(
        (item) =>
          item.id.toLowerCase().includes(search.toLowerCase()) ||
          item.code_snippet.toLowerCase().includes(search.toLowerCase())
      )
    : items;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border-subtle">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-indigo-400" />
            <span>Review History</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Persisted review records from MongoDB. Inspect past code submissions and findings.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => fetchHistory()}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-background-surface hover:bg-background-hover text-slate-300 border border-border-subtle text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
            title="Refresh history"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <Link
            to="/review"
            className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-sm shadow-indigo-950"
          >
            New Review
          </Link>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 text-xs">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search in history items..."
            className="w-full pl-8 pr-3 py-1.5 bg-background-surface border border-border-subtle rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/80"
          />
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <span>Per page:</span>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="bg-background-surface border border-border-subtle rounded px-2 py-1 text-slate-300 focus:outline-none"
            aria-label="Items per page"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <Alert
          type="error"
          title="Failed to Load History"
          message={error.message}
          code={error.code}
          onRetry={() => fetchHistory()}
        />
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="p-4 rounded-xl border border-border-subtle bg-background-card flex items-center justify-between">
              <div className="space-y-2 flex-1">
                <Skeleton className="w-48 h-4" />
                <Skeleton className="w-3/4 h-3" />
              </div>
              <Skeleton className="w-20 h-6" />
            </div>
          ))}
        </div>
      )}

      {/* Content List */}
      {!loading && !error && (
        <>
          {filteredItems.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border-muted p-12 text-center bg-background-card/40 space-y-3">
              <History className="w-10 h-10 text-slate-500 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-200">No Review History Found</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                {search
                  ? 'No historical reviews match your search query.'
                  : 'Completed code reviews will be stored in MongoDB and listed here once persistence is enabled.'}
              </p>
              <Link
                to="/review"
                className="inline-block mt-2 text-xs font-medium text-indigo-400 hover:text-indigo-300 underline"
              >
                Run your first code review &rarr;
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredItems.map((item) => {
                const dateStr = new Date(item.submitted_at).toLocaleString(undefined, {
                  dateStyle: 'medium',
                  timeStyle: 'short',
                });
                const totalFindings =
                  item.finding_counts.critical +
                  item.finding_counts.high +
                  item.finding_counts.medium +
                  item.finding_counts.low +
                  item.finding_counts.info;

                return (
                  <div
                    key={item.id}
                    className="p-4 sm:p-5 rounded-xl border border-border-subtle bg-background-card hover:border-border-muted transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                  >
                    <div className="space-y-2 flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className="font-mono font-semibold text-slate-200 flex items-center gap-1">
                          <Hash className="w-3.5 h-3.5 text-indigo-400" />
                          {item.id.substring(0, 8)}...
                        </span>
                        <span className="text-slate-600">•</span>
                        <span className="text-slate-400 flex items-center gap-1 font-mono text-[11px]">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          {dateStr}
                        </span>
                        <span className="text-slate-600">•</span>
                        <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono text-[10px]">
                          {item.language}
                        </span>
                      </div>

                      {/* Code Snippet preview */}
                      <pre className="text-xs font-mono text-slate-300 bg-black/30 p-2.5 rounded border border-border-subtle/50 overflow-x-auto whitespace-pre-wrap max-h-16">
                        {item.code_snippet}
                      </pre>
                    </div>

                    {/* Finding Counts Pills */}
                    <div className="flex items-center gap-2 shrink-0">
                      <div className="flex items-center gap-1 text-[11px] font-mono">
                        {item.finding_counts.critical > 0 && (
                          <span className="px-1.5 py-0.5 rounded bg-red-950/80 text-red-400 border border-red-800/40" title="Critical">
                            {item.finding_counts.critical}C
                          </span>
                        )}
                        {item.finding_counts.high > 0 && (
                          <span className="px-1.5 py-0.5 rounded bg-orange-950/80 text-orange-400 border border-orange-800/40" title="High">
                            {item.finding_counts.high}H
                          </span>
                        )}
                        {item.finding_counts.medium > 0 && (
                          <span className="px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/40" title="Medium">
                            {item.finding_counts.medium}M
                          </span>
                        )}
                        {item.finding_counts.low > 0 && (
                          <span className="px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800/40" title="Low">
                            {item.finding_counts.low}L
                          </span>
                        )}
                        {totalFindings === 0 && (
                          <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                            Clean
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination Controls */}
          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-border-subtle text-xs text-slate-400">
              <div>
                Showing page <strong className="text-slate-200">{data.page}</strong> of{' '}
                <strong className="text-slate-200">{data.total_pages}</strong> ({data.total} total reviews)
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page <= 1}
                  className="px-2.5 py-1.5 rounded bg-background-surface hover:bg-background-hover text-slate-300 border border-border-subtle disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page >= data.total_pages}
                  className="px-2.5 py-1.5 rounded bg-background-surface hover:bg-background-hover text-slate-300 border border-border-subtle disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
