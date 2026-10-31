import React, { useState } from 'react';
import { Check, Copy, FileDiff, AlertCircle } from 'lucide-react';
import type { Patch } from '../../types/review';

interface PatchDiffProps {
  patch: Patch;
  className?: string;
}

export const PatchDiff: React.FC<PatchDiffProps> = ({ patch, className = '' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(patch.suggested);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`rounded-lg border border-border-subtle bg-background-subtle/80 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2 bg-slate-900/60 border-b border-border-subtle text-xs">
        <div className="flex items-center gap-1.5 font-medium text-slate-300">
          <FileDiff className="w-3.5 h-3.5 text-indigo-400" />
          <span>Suggested Code Patch</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            title="Copy suggested code to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-400" />
                <span className="text-emerald-300">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3 text-slate-400" />
                <span>Copy Fix</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Diff comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border-subtle text-xs font-mono">
        {/* Original */}
        <div className="p-3 bg-red-950/20">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-red-400/80 mb-1.5 flex items-center justify-between">
            <span>Original Code</span>
            <span className="text-red-400 font-mono font-bold">-</span>
          </div>
          <pre className="overflow-x-auto text-red-200/90 whitespace-pre-wrap break-words leading-relaxed">
            {patch.original}
          </pre>
        </div>

        {/* Suggested */}
        <div className="p-3 bg-emerald-950/20">
          <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-emerald-400/80 mb-1.5 flex items-center justify-between">
            <span>Suggested Replacement</span>
            <span className="text-emerald-400 font-mono font-bold">+</span>
          </div>
          <pre className="overflow-x-auto text-emerald-200/90 whitespace-pre-wrap break-words leading-relaxed">
            {patch.suggested}
          </pre>
        </div>
      </div>

      {/* Safety Notice Footer */}
      <div className="px-3 py-1.5 bg-black/40 border-t border-border-subtle/60 flex items-center gap-1.5 text-[11px] text-slate-400">
        <AlertCircle className="w-3 h-3 text-amber-400/80 shrink-0" />
        <span>Display-only suggested fix. Review carefully; patches are never automatically executed or applied.</span>
      </div>
    </div>
  );
};
