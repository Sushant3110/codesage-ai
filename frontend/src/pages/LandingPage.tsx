import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Code2,
  Sparkles,
  ArrowRight,
  Database,
} from 'lucide-react';
import { apiClient } from '../api/client';
import type { CapabilitiesResponse } from '../types/review';
import { SAMPLE_SNIPPETS } from '../data/sampleCode';

export const LandingPage: React.FC = () => {
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse | null>(null);
  const [activeSnippetIndex, setActiveSnippetIndex] = useState(0);

  useEffect(() => {
    apiClient.getCapabilities().then(setCapabilities).catch(() => {});
  }, []);

  const activeSnippet = SAMPLE_SNIPPETS[activeSnippetIndex];

  return (
    <div className="flex flex-col min-h-[calc(100vh-3.5rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 sm:pt-24 sm:pb-28 border-b border-border-subtle bg-gradient-to-b from-background-subtle via-background to-background">
        {/* Subtle grid background */}
        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(#6366f1 1px, transparent 1px)`,
            backgroundSize: '24px 24px',
          }}
        />

        <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10 text-center">
          {/* Top Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-indigo-950/60 text-indigo-300 border border-indigo-700/40 mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Multi-Language Review • ChromaDB RAG Grounding • Gemini Analysis</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-100 tracking-tight max-w-4xl mx-auto leading-[1.15]">
            Catch critical software bugs with{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-violet-300 to-indigo-200">
              grounded AI code review
            </span>
            .
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Eliminate security vulnerabilities, buffer overflows, and architectural traps.
            Backed by semantic vector retrieval over approved OWASP, ISO C, and language standards.
          </p>

          {/* CTA Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/review"
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-950 hover:shadow-indigo-900"
            >
              <span>Launch Review Workspace</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/history"
              className="w-full sm:w-auto px-6 py-3 rounded-lg bg-background-surface hover:bg-background-hover text-slate-200 border border-border-subtle font-medium text-sm flex items-center justify-center gap-2 transition-colors"
            >
              <span>View Review History</span>
            </Link>
          </div>

          {/* Capabilities Bar */}
          {capabilities && (
            <div className="mt-12 inline-flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-400 px-4 py-2 rounded-lg bg-background-card/80 border border-border-subtle">
              <span className="flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5 text-indigo-400" />
                Languages: <strong className="text-slate-200">{capabilities.supported_languages.length} Supported (Python, Java, JS, TS, C/C++, SQL, HTML, CSS)</strong>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-indigo-400" />
                RAG Store:{' '}
                <strong className="text-slate-200">
                  {capabilities.rag_enabled ? `ChromaDB (${capabilities.rag_document_count} chunks)` : 'Disabled'}
                </strong>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Model: <strong className="text-slate-200">{capabilities.llm_model}</strong>
              </span>
            </div>
          )}
        </div>
      </section>

      {/* Workflow Explanation (How it works) */}
      <section className="py-16 sm:py-20 border-b border-border-subtle bg-background-subtle">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight">
              Architected for safety and deterministic rigor
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Unlike generic chatbot wrappers, CodeSage AI enforces strict safety boundaries and never executes submitted code.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1 */}
            <div className="rounded-xl border border-border-subtle bg-background-card p-6 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-mono font-bold text-sm">
                01
              </div>
              <h3 className="text-base font-semibold text-slate-100">Sandboxed Static Analysis</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Source code is validated against 32KB limits and analyzed by AST rules (Ruff & Bandit). Zero execution in backend processes.
              </p>
            </div>

            {/* Step 2 */}
            <div className="rounded-xl border border-border-subtle bg-background-card p-6 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400 font-mono font-bold text-sm">
                02
              </div>
              <h3 className="text-base font-semibold text-slate-100">ChromaDB RAG Grounding</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Code patterns are queried against local vector embeddings (<code className="text-indigo-300">all-MiniLM-L6-v2</code>) indexing PEP 8 and OWASP guidelines.
              </p>
            </div>

            {/* Step 3 */}
            <div className="rounded-xl border border-border-subtle bg-background-card p-6 space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-mono font-bold text-sm">
                03
              </div>
              <h3 className="text-base font-semibold text-slate-100">Grounded Patch Proposals</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Structured findings include severity, evidence, line references, and display-only diff comparisons. Patches are never auto-applied.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Sample Preview */}
      <section className="py-16 sm:py-20 bg-background">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-indigo-400">
                Live Interactive Examples
              </span>
              <h2 className="text-2xl font-bold text-slate-100 tracking-tight mt-1">
                Explore real review scenarios
              </h2>
            </div>

            {/* Snippet selector tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
              {SAMPLE_SNIPPETS.map((snippet, idx) => (
                <button
                  key={snippet.id}
                  onClick={() => setActiveSnippetIndex(idx)}
                  className={`px-3 py-1.5 rounded-md font-medium transition-colors shrink-0 ${
                    activeSnippetIndex === idx
                      ? 'bg-slate-800 text-indigo-300 border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  {snippet.name.split(' (')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Preview Box */}
          <div className="rounded-xl border border-border-subtle bg-background-card overflow-hidden shadow-xl shadow-black/40">
            <div className="px-4 py-3 bg-background-surface/80 border-b border-border-subtle flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
                <span className="ml-2 font-mono text-slate-400">sample_input.py</span>
              </div>
              <Link
                to="/review"
                className="text-indigo-400 hover:text-indigo-300 text-xs font-medium flex items-center gap-1"
              >
                Review in Workspace <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="p-4 sm:p-6 bg-[#0a0e1a] font-mono text-xs overflow-x-auto leading-relaxed text-slate-300 max-h-80">
              <pre>{activeSnippet.code}</pre>
            </div>

            <div className="p-4 bg-background-surface/40 border-t border-border-subtle flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Expected Detections:</span>
                {activeSnippet.expectedIssueTypes.map((type, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40 font-mono text-[11px]"
                  >
                    {type}
                  </span>
                ))}
              </div>
              <span className="text-slate-500 text-[11px]">Demo Input • Sandboxed</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
