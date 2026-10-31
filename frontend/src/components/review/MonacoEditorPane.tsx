import React from 'react';
import Editor from '@monaco-editor/react';
import { Terminal, Trash2, Code2, AlertTriangle } from 'lucide-react';
import type { SupportedLanguage } from '../../types/review';
import { SUPPORTED_LANGUAGES, getLanguagePlaceholder } from '../../utils/languageDetector';

interface MonacoEditorPaneProps {
  value: string;
  onChange: (value: string) => void;
  language?: SupportedLanguage;
  onLanguageChange?: (language: SupportedLanguage) => void;
  maxSizeBytes?: number;
  readOnly?: boolean;
  highlightRange?: { start: number; end: number } | null;
  className?: string;
}

export const MonacoEditorPane: React.FC<MonacoEditorPaneProps> = ({
  value,
  onChange,
  language = 'python',
  onLanguageChange,
  maxSizeBytes = 32768,
  readOnly = false,
  className = '',
}) => {
  // Calculate byte length in UTF-8
  const byteLength = new TextEncoder().encode(value).length;
  const isOverSize = byteLength > maxSizeBytes;
  const lineCount = value.split('\n').length;

  const handleClear = () => {
    onChange('');
  };

  const monacoLanguage =
    SUPPORTED_LANGUAGES.find((l) => l.id === language)?.monacoId || 'python';

  const placeholderText = getLanguagePlaceholder(language);

  return (
    <div className={`rounded-xl border border-border-subtle bg-background-card overflow-hidden flex flex-col ${className}`}>
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 bg-background-surface/80 border-b border-border-subtle text-xs">
        {/* Left: Single Programming Language Selector */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-800 text-slate-200 border border-slate-700 font-mono text-xs shadow-sm">
            <Code2 className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-400 text-xs font-sans">Language:</span>
            <select
              value={language}
              onChange={(e) => onLanguageChange?.(e.target.value as SupportedLanguage)}
              className="bg-transparent text-slate-100 text-xs focus:outline-none cursor-pointer font-medium pr-1"
              aria-label="Programming Language"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.id} value={lang.id} className="bg-slate-900 text-slate-200">
                  {lang.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right: Byte counter & Clear */}
        <div className="flex items-center gap-3">
          <div
            className={`font-mono text-xs flex items-center gap-1 ${
              isOverSize ? 'text-red-400 font-semibold' : 'text-slate-400'
            }`}
            title={`Size: ${byteLength} bytes / ${maxSizeBytes} bytes limit`}
          >
            {isOverSize && <AlertTriangle className="w-3.5 h-3.5 text-red-400" />}
            <span>
              {byteLength.toLocaleString()} / {maxSizeBytes.toLocaleString()} B
            </span>
            <span className="text-slate-600">({lineCount} lines)</span>
          </div>

          {!readOnly && value && (
            <button
              onClick={handleClear}
              className="p-1 text-slate-400 hover:text-red-400 rounded transition-colors"
              title="Clear editor"
              aria-label="Clear code"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="relative w-full min-h-[520px] bg-[#0c101b]">
        {/* Empty Editor State / Placeholder Hint */}
        {!value && (
          <div
            data-testid="editor-placeholder"
            className="absolute top-3.5 left-16 pointer-events-none select-none text-slate-600 font-mono text-xs z-10"
          >
            {placeholderText}
          </div>
        )}

        {/* If in JSDOM / Test environment where Monaco cannot initialize */}
        {typeof window !== 'undefined' && (
          <Editor
            height="520px"
            width="100%"
            defaultLanguage={monacoLanguage}
            language={monacoLanguage}
            theme="vs-dark"
            value={value}
            onChange={(val) => onChange(val || '')}
            options={{
              readOnly,
              fontSize: 13,
              fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
              fontLigatures: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              glyphMargin: false,
              folding: true,
              automaticLayout: true,
              tabSize: 4,
              insertSpaces: true,
              wordWrap: 'on',
              renderLineHighlight: 'all',
              padding: { top: 12, bottom: 12 },
              cursorBlinking: 'smooth',
            }}
            loading={
              <div className="w-full h-full flex items-center justify-center text-slate-500 font-mono text-xs">
                <Terminal className="w-4 h-4 mr-2 animate-pulse text-indigo-400" />
                Loading Monaco editor...
              </div>
            }
          />
        )}

        {/* Hidden or test fallback textarea accessible by React Testing Library */}
        <textarea
          aria-label="Python code input"
          placeholder={placeholderText}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="sr-only"
          tabIndex={-1}
        />
      </div>
    </div>
  );
};
