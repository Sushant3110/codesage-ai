import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import type { Citation } from '../../types/review';

interface CitationBadgeProps {
  citation: Citation;
  className?: string;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({ citation, className = '' }) => {
  const [expanded, setExpanded] = useState(false);
  const scorePercent = Math.round(citation.relevance_score * 100);

  return (
    <div className={`rounded-md border border-border-subtle bg-slate-900/70 p-2.5 text-xs ${className}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-1.5 font-medium text-slate-200">
              <span>{citation.document_title}</span>
              {citation.section && (
                <span className="text-slate-400 font-normal">
                  — <span className="text-slate-300 font-mono text-[11px]">{citation.section}</span>
                </span>
              )}
            </div>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5 flex items-center gap-2">
              <span>Source: {citation.source_file}</span>
              {citation.source_url && (
                <a
                  href={citation.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-400 hover:text-indigo-300 underline inline-flex items-center gap-0.5"
                  title="View authoritative guideline"
                >
                  docs <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Score & Toggle */}
        <div className="flex items-center gap-2 shrink-0">
          <span
            className="px-1.5 py-0.5 rounded font-mono text-[10px] font-semibold bg-indigo-950 text-indigo-300 border border-indigo-700/50"
            title={`Cosine similarity score: ${citation.relevance_score}`}
          >
            {scorePercent}% match
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
            aria-label={expanded ? 'Collapse citation text' : 'Expand citation text'}
          >
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Expanded chunk text */}
      {expanded && (
        <div className="mt-2.5 pt-2 border-t border-border-subtle/60 text-slate-300 font-mono text-[11px] leading-relaxed bg-black/30 p-2 rounded whitespace-pre-wrap break-words">
          {citation.chunk_text}
        </div>
      )}
    </div>
  );
};
