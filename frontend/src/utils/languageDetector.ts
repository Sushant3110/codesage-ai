/**
 * Language detection and registry utilities for CodeSage AI Frontend
 */

import type { SupportedLanguage } from '../types/review';

export interface LanguageOption {
  id: SupportedLanguage;
  label: string;
  monacoId: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { id: 'python', label: 'Python 3.11+', monacoId: 'python' },
  { id: 'java', label: 'Java', monacoId: 'java' },
  { id: 'javascript', label: 'JavaScript', monacoId: 'javascript' },
  { id: 'typescript', label: 'TypeScript', monacoId: 'typescript' },
  { id: 'c', label: 'C', monacoId: 'c' },
  { id: 'cpp', label: 'C++', monacoId: 'cpp' },
  { id: 'html', label: 'HTML', monacoId: 'html' },
  { id: 'css', label: 'CSS', monacoId: 'css' },
  { id: 'sql', label: 'SQL', monacoId: 'sql' },
];

export function detectLanguage(code: string): SupportedLanguage | null {
  const clean = code.trim();
  if (!clean) return null;

  // HTML
  if (/<!DOCTYPE\s+html/i.test(clean) || /<\s*(html|head|body|div|span|script|section|article)[\s>]/i.test(clean)) {
    return 'html';
  }

  // CSS
  if (/@(media|keyframes|import)\b/.test(clean) || /(?:^|[\r\n])\s*([.#]?[a-zA-Z0-9_-]+|\*)\s*\{[^}]*?(?:margin|padding|color|background|display|font)\s*:/i.test(clean)) {
    return 'css';
  }

  // SQL
  if (/\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|CREATE\s+TABLE|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b/i.test(clean)) {
    return 'sql';
  }

  // C++
  if (/#include\s*<(iostream|vector|string|memory|algorithm|map)>/.test(clean) || /\bstd::(cout|cin|vector|string|make_unique)\b/.test(clean) || /\b(cout\s*<<|cin\s*>>|nullptr)\b/.test(clean) || /\bnamespace\s+\w+\s*\{/.test(clean)) {
    return 'cpp';
  }

  // C
  if (/#include\s*<(stdio\.h|stdlib\.h|string\.h|unistd\.h)>/.test(clean) || /\b(printf|scanf|malloc|free)\s*\(/.test(clean)) {
    return 'c';
  }

  // Java
  if (/\bpublic\s+(class|interface|enum)\s+\w+/.test(clean) || /\bSystem\.out\.(println|print)\b/.test(clean) || /\bpublic\s+static\s+void\s+main\s*\(/.test(clean) || /\bimport\s+java\./.test(clean)) {
    return 'java';
  }

  // TypeScript
  if (/\binterface\s+\w+\s*\{/.test(clean) || /\btype\s+\w+\s*=/.test(clean) || /:\s*(string|number|boolean|any|unknown|void|Promise<[^>]+>)\b/.test(clean) || /\bas\s+(string|number|boolean|const)\b/.test(clean)) {
    return 'typescript';
  }

  // JavaScript
  if (/\bconsole\.(log|error|warn)\s*\(/.test(clean) || /\b(const|let|var)\s+\w+\s*=\s*(require\(|async\s*\(|function|\(|\[|\{)/.test(clean) || /=>\s*\{/.test(clean) || /\b(module\.exports|export\s+default)\b/.test(clean)) {
    return 'javascript';
  }

  // Python
  if (/^\s*def\s+\w+\s*\(/m.test(clean) || /^\s*class\s+\w+(?:\(.*\))?:\s*$/m.test(clean) || /^\s*(import\s+\w+|from\s+\w+\s+import)/m.test(clean) || /if\s+__name__\s*==\s*['"]__main__['"]/.test(clean) || /\bprint\s*\(/.test(clean)) {
    return 'python';
  }

  return null;
}

export function getLanguagePlaceholder(language: SupportedLanguage): string {
  switch (language) {
    case 'python':
      return 'Write or paste your Python code here...';
    case 'java':
      return 'Write or paste your Java code here...';
    case 'javascript':
      return 'Write or paste your JavaScript code here...';
    case 'typescript':
      return 'Write or paste your TypeScript code here...';
    case 'c':
      return 'Write or paste your C source code here...';
    case 'cpp':
      return 'Write or paste your C++ source code here...';
    case 'html':
      return 'Write or paste your HTML markup here...';
    case 'css':
      return 'Write or paste your CSS stylesheet here...';
    case 'sql':
      return 'Write or paste your SQL queries here...';
    default:
      return 'Write or paste your source code here...';
  }
}
