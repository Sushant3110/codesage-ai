import React, { useState } from 'react';
import { Play, Sparkles, RefreshCw, CheckCircle2 } from 'lucide-react';
import { apiClient, ApiError } from '../api/client';
import type { Category, Finding, ReviewResponse, Severity, SupportedLanguage } from '../types/review';
import { MonacoEditorPane } from '../components/review/MonacoEditorPane';
import { ReviewSummaryCard } from '../components/review/ReviewSummaryCard';
import { SeverityFilter } from '../components/review/SeverityFilter';
import { FindingCard } from '../components/review/FindingCard';
import { Alert } from '../components/ui/Alert';
import { FindingCardSkeleton, ReviewSummarySkeleton } from '../components/ui/Skeleton';

interface WorkspacePageProps {
  initialCode?: string;
  initialContext?: string;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({
  initialCode = '',
  initialContext = '',
}) => {
  const [code, setCode] = useState<string>(initialCode);
  const [context, setContext] = useState<string>(initialContext);
  const [language, setLanguage] = useState<SupportedLanguage>('python');
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [error, setError] = useState<{ status: number; code: string; message: string } | null>(null);

  // Filters
  const [activeSeverity, setActiveSeverity] = useState<Severity | 'all'>('all');
  const [activeCategory, setActiveCategory] = useState<Category | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const maxSizeBytes = 32768;
  const byteLength = new TextEncoder().encode(code).length;
  const isOverSize = byteLength > maxSizeBytes;

  const handleReviewSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!code.trim()) {
      setError({
        status: 422,
        code: 'VALIDATION_ERROR',
        message: 'Source code cannot be empty. Paste or write code to review.',
      });
      return;
    }

    if (isOverSize) {
      setError({
        status: 413,
        code: 'PAYLOAD_TOO_LARGE',
        message: `Submitted code is ${byteLength.toLocaleString()} bytes, which exceeds the maximum limit of ${maxSizeBytes.toLocaleString()} bytes.`,
      });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.submitReview({
        code,
        language,
        context: context.trim() ? context.trim() : null,
      });
      setReview(response);
      setActiveSeverity('all');
      setActiveCategory('all');
      setSearchQuery('');
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
          code: 'UNEXPECTED_ERROR',
          message: err instanceof Error ? err.message : 'An unexpected error occurred during review.',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // Filter findings
  const filteredFindings: Finding[] = review
    ? review.findings.filter((f) => {
        if (activeSeverity !== 'all' && f.severity !== activeSeverity) return false;
        if (activeCategory !== 'all' && f.category !== activeCategory) return false;
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matches =
            f.title.toLowerCase().includes(q) ||
            f.explanation.toLowerCase().includes(q) ||
            (f.evidence && f.evidence.toLowerCase().includes(q)) ||
            (f.rule_id && f.rule_id.toLowerCase().includes(q));
          if (!matches) return false;
        }
        return true;
      })
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
      {/* Top Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border-subtle">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Code Review Workspace</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Submit source code across 9 supported languages for structured vulnerability, correctness, and style analysis.
          </p>
        </div>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => handleReviewSubmit()}
            disabled={loading || !code.trim() || isOverSize}
            className="w-full sm:w-auto px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-xs sm:text-sm flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-950"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Analyzing Code...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Code Review</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Split Layout: Editor (Left) & Results (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Monaco Editor + Context (5 cols on large screens) */}
        <div className="lg:col-span-5 space-y-4">
          <MonacoEditorPane
            value={code}
            onChange={setCode}
            language={language}
            onLanguageChange={setLanguage}
            maxSizeBytes={maxSizeBytes}
          />

          {/* Optional Review Context Input */}
          <div className="rounded-xl border border-border-subtle bg-background-card p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label htmlFor="context-input" className="font-medium text-slate-300">
                Optional Context / Intent
              </label>
              <span className={`font-mono text-[11px] ${context.length > 500 ? 'text-red-400 font-bold' : 'text-slate-500'}`}>
                {context.length} / 500
              </span>
            </div>
            <textarea
              id="context-input"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              maxLength={500}
              rows={2}
              placeholder="e.g. Ingestion service handling batch user metrics from untrusted CSV..."
              className="w-full px-3 py-2 text-xs bg-background-surface border border-border-subtle rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/80 resize-none transition-colors"
            />
          </div>
        </div>

        {/* Right Column: Results & Findings (7 cols on large screens) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Error Alert */}
          {error && (
            <Alert
              type="error"
              title={
                error.status === 413
                  ? 'Code Payload Too Large'
                  : error.status === 422
                  ? 'Input Validation Error'
                  : error.status === 503
                  ? 'Service Temporarily Unavailable'
                  : error.status === 0
                  ? 'Network Connection Failure'
                  : 'Review Execution Error'
              }
              message={error.message}
              code={error.code}
              onRetry={() => handleReviewSubmit()}
              onDismiss={() => setError(null)}
            />
          )}

          {/* Loading State Skeleton */}
          {loading && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-900/40 text-xs text-indigo-300 flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Executing sandboxed AST parsing, ChromaDB guideline retrieval, and LLM verification...</span>
              </div>
              <ReviewSummarySkeleton />
              <FindingCardSkeleton />
              <FindingCardSkeleton />
            </div>
          )}

          {/* Empty Initial State */}
          {!loading && !review && !error && (
            <div className="rounded-xl border border-dashed border-border-muted p-12 text-center bg-background-card/40 flex flex-col items-center justify-center space-y-3">
              <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400">
                <Sparkles className="w-6 h-6 text-indigo-400" />
              </div>
              <h3 className="text-base font-semibold text-slate-200">No Review Run Yet</h3>
              <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
                Paste Python code into the editor or select a sample snippet, then click{' '}
                <strong className="text-slate-300">Run Code Review</strong> to analyze for vulnerabilities and guideline violations.
              </p>
            </div>
          )}

          {/* Review Results */}
          {!loading && review && (
            <div className="space-y-4">
              {/* Summary Card */}
              <ReviewSummaryCard review={review} />

              {/* Severity & Category Filter Bar */}
              <SeverityFilter
                counts={review.finding_counts}
                total={review.findings.length}
                activeSeverity={activeSeverity}
                activeCategory={activeCategory}
                searchQuery={searchQuery}
                onSelectSeverity={setActiveSeverity}
                onSelectCategory={setActiveCategory}
                onSearchChange={setSearchQuery}
              />

              {/* Clean Code (0 findings total) */}
              {review.findings.length === 0 && (
                <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-8 text-center space-y-2">
                  <div className="w-10 h-10 rounded-full bg-emerald-900/40 border border-emerald-700/50 flex items-center justify-center mx-auto text-emerald-400">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-semibold text-emerald-200">Clean Code Verified</h3>
                  <p className="text-xs text-emerald-400/80 max-w-sm mx-auto">
                    No critical vulnerabilities, bugs, or PEP 8 violations were detected in the submitted snippet.
                  </p>
                </div>
              )}

              {/* No Findings matching active filter */}
              {review.findings.length > 0 && filteredFindings.length === 0 && (
                <div className="rounded-xl border border-border-subtle bg-background-card p-8 text-center text-xs text-slate-400">
                  <span>No findings match the current filter or search criteria.</span>
                </div>
              )}

              {/* Findings List */}
              <div className="space-y-4" data-testid="findings-list">
                {filteredFindings.map((finding) => (
                  <FindingCard key={finding.id} finding={finding} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
