import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileQuestion } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4">
      <div className="max-w-md w-full rounded-xl border border-border-subtle bg-background-card p-8 text-center space-y-4 shadow-lg shadow-black/40">
        <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-slate-400">
          <FileQuestion className="w-6 h-6 text-indigo-400" />
        </div>
        <h1 className="text-xl font-bold text-slate-100">Page Not Found</h1>
        <p className="text-xs text-slate-400 leading-relaxed">
          The requested route does not exist. Return to the code review workspace or explore past submissions.
        </p>
        <div className="pt-2">
          <Link
            to="/review"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-sm shadow-indigo-950"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Workspace</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
