import React from 'react';
import { CheckCircle2, ShieldCheck, Database, Calendar, Hash, FileCode } from 'lucide-react';
import type { ReviewResponse } from '../../types/review';

interface ReviewSummaryCardProps {
  review: ReviewResponse;
  className?: string;
}

export const ReviewSummaryCard: React.FC<ReviewSummaryCardProps> = ({ review, className = '' }) => {
  const dateFormatted = new Date(review.submitted_at).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  const totalFindings = review.findings.length;

  return (
    <div className={`rounded-xl border border-border-subtle bg-background-card p-5 space-y-4 shadow-sm ${className}`}>
      {/* Top row: Title + Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <FileCode className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100 tracking-tight">Review Assessment</h2>
            <div className="flex items-center gap-2 text-xs text-slate-400 font-mono mt-0.5">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-500" />
                {dateFormatted}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1" title={`Code Hash: ${review.code_hash}`}>
                <Hash className="w-3 h-3 text-slate-500" />
                {review.code_hash.substring(0, 8)}
              </span>
            </div>
          </div>
        </div>

        {/* Feature status badges */}
        <div className="flex items-center gap-2">
          {review.rag_context_retrieved && (
            <span
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-mono bg-indigo-950/70 text-indigo-300 border border-indigo-700/50"
              title="Guidelines retrieved from ChromaDB vector store"
            >
              <Database className="w-3 h-3 text-indigo-400" />
              RAG Grounded
            </span>
          )}
          {review.static_analysis_ran && (
            <span
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-950/70 text-emerald-300 border border-emerald-700/50"
              title="Static analysis executed"
            >
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              Static Analysis
            </span>
          )}
        </div>
      </div>

      {/* Summary statement */}
      <p className="text-sm text-slate-300 leading-relaxed bg-background-surface/50 p-3.5 rounded-lg border border-border-subtle/60">
        {review.summary || 'Review completed. See individual findings below.'}
      </p>

      {/* Severity Count Summary Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 pt-1">
        <div className="p-3 rounded-lg bg-red-950/20 border border-red-900/40">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-red-400/90">Critical</div>
          <div className="text-xl font-bold font-mono text-red-300 mt-0.5">{review.finding_counts.critical}</div>
        </div>
        <div className="p-3 rounded-lg bg-orange-950/20 border border-orange-900/40">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-orange-400/90">High</div>
          <div className="text-xl font-bold font-mono text-orange-300 mt-0.5">{review.finding_counts.high}</div>
        </div>
        <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-900/40">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-amber-400/90">Medium</div>
          <div className="text-xl font-bold font-mono text-amber-300 mt-0.5">{review.finding_counts.medium}</div>
        </div>
        <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-900/40">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-blue-400/90">Low</div>
          <div className="text-xl font-bold font-mono text-blue-300 mt-0.5">{review.finding_counts.low}</div>
        </div>
        <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/40 col-span-2 sm:col-span-1">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-slate-400">Total Findings</div>
          <div className="text-xl font-bold font-mono text-slate-200 mt-0.5 flex items-center justify-between">
            <span>{totalFindings}</span>
            {totalFindings === 0 && <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />}
          </div>
        </div>
      </div>
    </div>
  );
};
