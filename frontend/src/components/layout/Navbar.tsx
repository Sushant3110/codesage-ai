import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Code2, History, Sparkles, AlertCircle } from 'lucide-react';
import { apiClient } from '../../api/client';
import type { CapabilitiesResponse } from '../../types/review';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [capabilities, setCapabilities] = useState<CapabilitiesResponse | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const checkStatus = async () => {
      try {
        const caps = await apiClient.getCapabilities();
        if (mounted) {
          setCapabilities(caps);
          setBackendOnline(true);
        }
      } catch {
        if (mounted) {
          setBackendOnline(false);
        }
      }
    };
    checkStatus();
    return () => {
      mounted = false;
    };
  }, []);

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border-subtle bg-background/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center gap-6">
          <Link
            to="/"
            className="flex items-center gap-2.5 text-slate-100 hover:text-white transition-colors group"
          >
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:border-indigo-400/50 transition-colors shadow-sm shadow-indigo-950">
              <Sparkles className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-sm tracking-tight text-slate-100 flex items-center gap-1.5">
                CodeSage <span className="text-xs px-1.5 py-0.2 rounded font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">AI</span>
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-1 text-xs font-medium">
            <Link
              to="/review"
              className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 ${
                isActive('/review')
                  ? 'bg-slate-800 text-indigo-300 border border-slate-700/60'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              Workspace
            </Link>
            <Link
              to="/history"
              className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 ${
                isActive('/history')
                  ? 'bg-slate-800 text-indigo-300 border border-slate-700/60'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              History
            </Link>
          </nav>
        </div>

        {/* Status indicator & info */}
        <div className="flex items-center gap-3">
          {backendOnline === true && capabilities ? (
            <div
              className="flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-mono bg-emerald-950/40 text-emerald-400 border border-emerald-800/50 shadow-sm"
              title={`Engine: ${capabilities.llm_model} | RAG: ${capabilities.rag_enabled ? `${capabilities.rag_document_count} chunks` : 'disabled'}`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="hidden sm:inline">API Online</span>
              {capabilities.rag_enabled && (
                <span className="text-[10px] px-1 rounded bg-emerald-900/60 text-emerald-300 border border-emerald-700/40">
                  RAG
                </span>
              )}
            </div>
          ) : backendOnline === false ? (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-red-950/40 text-red-400 border border-red-800/50"
              title="Backend API is unreachable at localhost:8000"
            >
              <AlertCircle className="w-3 h-3 text-red-400" />
              <span className="hidden sm:inline">API Offline</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-xs font-mono text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-600 animate-pulse" />
              Connecting...
            </div>
          )}

          <Link
            to="/review"
            className="text-xs font-medium px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-sm shadow-indigo-950 flex items-center gap-1.5"
          >
            Review Code
          </Link>
        </div>
      </div>
    </header>
  );
};
