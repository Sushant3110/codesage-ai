import React from 'react';
import { Terminal, AlignLeft, ShieldAlert } from 'lucide-react';
import type { Finding } from '../../types/review';
import { CategoryBadge, SeverityBadge, SourceBadge, VerificationBadge } from '../ui/Badge';
import { PatchDiff } from './PatchDiff';
import { CitationBadge } from './CitationBadge';

interface FindingCardProps {
  finding: Finding;
  onSelectLine?: (start: number, end: number) => void;
  className?: string;
}

export const FindingCard: React.FC<FindingCardProps> = ({
  finding,
  onSelectLine,
  className = '',
}) => {
  return (
    <article
      className={`rounded-xl border border-border-subtle bg-background-card hover:border-border-muted transition-all duration-200 overflow-hidden shadow-sm shadow-black/20 ${className}`}
      data-testid={`finding-${finding.id}`}
    >
      {/* Header bar */}
      <div className="p-4 sm:p-5 border-b border-border-subtle bg-background-surface/30">
        <div className="flex flex-wrap items-center justify-between gap-2.5 mb-2.5">
          <div className="flex flex-wrap items-center gap-2">
            <SeverityBadge severity={finding.severity} />
            <CategoryBadge category={finding.category} />
            <SourceBadge source={finding.source} ruleId={finding.rule_id} />
            <VerificationBadge status={finding.verification_status} />
          </div>

          {finding.line_range && (
            <button
              onClick={() => onSelectLine?.(finding.line_range!.start, finding.line_range!.end)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
              title="Click to view line in code editor"
            >
              <AlignLeft className="w-3 h-3 text-indigo-400" />
              <span>
                {finding.line_range.start === finding.line_range.end
                  ? `Line ${finding.line_range.start}`
                  : `Lines ${finding.line_range.start}–${finding.line_range.end}`}
              </span>
            </button>
          )}
        </div>

        {/* Title */}
        <h3 className="text-base font-semibold text-slate-100 tracking-tight leading-snug">
          {finding.title}
        </h3>
      </div>

      {/* Body */}
      <div className="p-4 sm:p-5 space-y-4">
        {/* Explanation */}
        <p className="text-sm text-slate-300 leading-relaxed">
          {finding.explanation}
        </p>

        {/* Evidence Block */}
        {finding.evidence && (
          <div className="rounded-lg bg-black/40 border border-border-subtle/70 p-3 text-xs">
            <div className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              <Terminal className="w-3 h-3 text-slate-500" />
              <span>Evidence / Matched Code</span>
            </div>
            <pre className="font-mono text-slate-200 overflow-x-auto whitespace-pre-wrap break-words">
              {finding.evidence}
            </pre>
          </div>
        )}

        {/* Suggested Patch */}
        {finding.patch && (
          <PatchDiff patch={finding.patch} />
        )}

        {/* Grounding RAG Citations */}
        {finding.citations && finding.citations.length > 0 && (
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400 uppercase tracking-wider">
              <ShieldAlert className="w-3 h-3 text-indigo-400" />
              <span>Authoritative Guideline Citations ({finding.citations.length})</span>
            </div>
            <div className="space-y-2">
              {finding.citations.map((citation, idx) => (
                <CitationBadge key={`${citation.source_file}-${idx}`} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>
    </article>
  );
};
