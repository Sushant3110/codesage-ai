import React from 'react';
import { Shield, Lock, Terminal } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-border-subtle bg-background-subtle py-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-slate-300 font-medium">
            <span>CodeSage AI</span>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400 font-mono text-[11px]">v0.1.0</span>
          </div>
          <div className="hidden sm:flex items-center gap-3 text-slate-500">
            <span className="inline-flex items-center gap-1">
              <Shield className="w-3 h-3 text-indigo-400" /> Sandboxed Analysis
            </span>
            <span>•</span>
            <span className="inline-flex items-center gap-1">
              <Lock className="w-3 h-3 text-emerald-400" /> Untrusted Input Boundary
            </span>
            <span>•</span>
            <span className="inline-flex items-center gap-1">
              <Terminal className="w-3 h-3 text-slate-400" /> Zero Code Execution
            </span>
          </div>
        </div>

        <div className="text-slate-500 text-center md:text-right">
          <span>Python Code Review with ChromaDB RAG & Gemini</span>
        </div>
      </div>
    </footer>
  );
};
