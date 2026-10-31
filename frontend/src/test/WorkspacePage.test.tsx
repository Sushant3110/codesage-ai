import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { WorkspacePage } from '../pages/WorkspacePage';
import { apiClient, ApiError } from '../api/client';
import type { ReviewResponse } from '../types/review';

// Mock apiClient
vi.mock('../api/client', () => {
  return {
    apiClient: {
      submitReview: vi.fn(),
    },
    ApiError: class extends Error {
      status: number;
      code: string;
      detail: string;
      constructor(status: number, code: string, detail: string) {
        super(detail);
        this.status = status;
        this.code = code;
        this.detail = detail;
      }
    },
  };
});

const mockReviewResponse: ReviewResponse = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  submitted_at: '2026-10-30T12:00:00Z',
  code_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  language: 'python',
  summary: 'Code review identified one high-severity injection flaw and minor style issues.',
  findings: [
    {
      id: 'f-1',
      source: 'llm',
      severity: 'high',
      category: 'security',
      rule_id: 'SEC-001',
      title: 'Command Injection detected',
      explanation: 'User input is passed directly to os.system without validation.',
      evidence: 'os.system("ping -c 1 " + user_ip)',
      line_range: { start: 28, end: 28 },
      patch: {
        original: 'os.system("ping -c 1 " + user_ip)',
        suggested: 'subprocess.run(["ping", "-c", "1", user_ip], check=True)',
      },
      citations: [
        {
          document_title: 'OWASP Secure Coding Cheat Sheet',
          chunk_text: 'Avoid shell=True and direct string command execution...',
          source_file: 'owasp_security.md',
          relevance_score: 0.94,
          source_url: 'https://owasp.org',
          section: 'Command Injection Prevention',
        },
      ],
      verification_status: 'unverified',
    },
    {
      id: 'f-2',
      source: 'ruff',
      severity: 'info',
      category: 'style',
      rule_id: 'E501',
      title: 'Line too long (92 > 79 characters)',
      explanation: 'Line exceeds maximum recommended line length in PEP 8.',
      evidence: 'subprocess.Popen(f"tar -czf /backups/data.tar.gz {backup_target}", shell=True)',
      line_range: { start: 40, end: 40 },
      patch: null,
      citations: [],
      verification_status: 'deterministic',
    },
  ],
  static_analysis_ran: true,
  rag_context_retrieved: true,
  finding_counts: {
    critical: 0,
    high: 1,
    medium: 0,
    low: 0,
    info: 1,
  },
};

describe('WorkspacePage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders workspace with clean editor toolbar, language selector, and placeholder', () => {
    render(<WorkspacePage />);
    expect(screen.getByText('Code Review Workspace')).toBeInTheDocument();
    expect(screen.getByText('Language:')).toBeInTheDocument();
    expect(screen.getByText('Python 3.11+')).toBeInTheDocument();
    expect(screen.getByTestId('editor-placeholder')).toHaveTextContent('Write or paste your Python code here...');
    expect(screen.getByRole('button', { name: /Run Code Review/i })).toBeInTheDocument();
  });

  it('displays all 9 supported languages in the selector and defaults to Python', () => {
    render(<WorkspacePage />);
    const select = screen.getByLabelText('Programming Language') as HTMLSelectElement;
    expect(select.value).toBe('python');

    const options = Array.from(select.options).map((o) => o.value);
    expect(options).toEqual([
      'python',
      'java',
      'javascript',
      'typescript',
      'c',
      'cpp',
      'html',
      'css',
      'sql',
    ]);
  });

  it('updates placeholder text when switching programming languages', () => {
    render(<WorkspacePage />);
    const select = screen.getByLabelText('Programming Language');

    fireEvent.change(select, { target: { value: 'java' } });
    expect(screen.getByTestId('editor-placeholder')).toHaveTextContent('Write or paste your Java code here...');

    fireEvent.change(select, { target: { value: 'sql' } });
    expect(screen.getByTestId('editor-placeholder')).toHaveTextContent('Write or paste your SQL queries here...');

    fireEvent.change(select, { target: { value: 'html' } });
    expect(screen.getByTestId('editor-placeholder')).toHaveTextContent('Write or paste your HTML markup here...');
  });

  it('preserves user-entered source code across language switches without deleting it', () => {
    render(<WorkspacePage />);
    const textarea = screen.getByLabelText('Python code input') as HTMLTextAreaElement;

    // Type custom code
    fireEvent.change(textarea, { target: { value: 'int x = 42;' } });
    expect(textarea.value).toBe('int x = 42;');

    // Switch language to Java
    const select = screen.getByLabelText('Programming Language');
    fireEvent.change(select, { target: { value: 'java' } });

    // Code MUST be preserved
    expect(textarea.value).toBe('int x = 42;');

    // Switch language to C++
    fireEvent.change(select, { target: { value: 'cpp' } });
    expect(textarea.value).toBe('int x = 42;');
  });

  it('disables submit button when code input is empty', () => {
    const spy = vi.spyOn(apiClient, 'submitReview');
    render(<WorkspacePage />);

    // Initially empty
    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    expect(submitBtn).toBeDisabled();
    expect(spy).not.toHaveBeenCalled();

    // Type and then clear
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: 'print("hi")' } });
    expect(submitBtn).not.toBeDisabled();

    fireEvent.change(textarea, { target: { value: '' } });
    expect(submitBtn).toBeDisabled();
    expect(spy).not.toHaveBeenCalled();
  });

  it('clears editor when clear button is clicked', () => {
    render(<WorkspacePage />);
    const textarea = screen.getByLabelText('Python code input') as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'const a = 10;' } });
    expect(textarea.value).toBe('const a = 10;');

    const clearBtn = screen.getByRole('button', { name: /Clear code/i });
    fireEvent.click(clearBtn);

    expect(textarea.value).toBe('');
    expect(screen.getByTestId('editor-placeholder')).toBeInTheDocument();
  });

  it('disables submit button and flags size warning when code is oversized (> 32KB)', () => {
    const spy = vi.spyOn(apiClient, 'submitReview');
    render(<WorkspacePage />);

    const oversizedCode = 'a = 1\n'.repeat(6000); // > 32KB
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: oversizedCode } });

    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    expect(submitBtn).toBeDisabled();
    expect(spy).not.toHaveBeenCalled();
    expect(screen.getByTitle(/36000 bytes/i)).toBeInTheDocument();
  });

  it('submits review successfully and renders findings, citations, and filters', async () => {
    const spy = vi.spyOn(apiClient, 'submitReview').mockResolvedValueOnce(mockReviewResponse);

    render(<WorkspacePage />);

    // Enter code to review
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: 'import os\nos.system("ping 127.0.0.1")\n' } });

    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    expect(spy).toHaveBeenCalledWith({
      code: 'import os\nos.system("ping 127.0.0.1")\n',
      language: 'python',
      context: null,
    });

    // Should render summary card
    expect(await screen.findByText(/Code review identified one high-severity injection/i)).toBeInTheDocument();
    expect(screen.getByText('RAG Grounded')).toBeInTheDocument();

    // Findings rendered
    expect(screen.getByText('Command Injection detected')).toBeInTheDocument();
    expect(screen.getByText('Line too long (92 > 79 characters)')).toBeInTheDocument();

    // Filter by high severity
    const highFilterBtn = screen.getByRole('button', { name: /High/i });
    fireEvent.click(highFilterBtn);

    expect(screen.getByText('Command Injection detected')).toBeInTheDocument();
    expect(screen.queryByText('Line too long (92 > 79 characters)')).not.toBeInTheDocument();

    // Reset filter
    const allFilterBtn = screen.getByRole('button', { name: /All/i });
    fireEvent.click(allFilterBtn);
    expect(screen.getByText('Line too long (92 > 79 characters)')).toBeInTheDocument();
  });

  it('submits review with selected language (e.g. Java)', async () => {
    const spy = vi.spyOn(apiClient, 'submitReview').mockResolvedValueOnce({
      ...mockReviewResponse,
      language: 'java',
      summary: 'Java code review completed.',
    });

    render(<WorkspacePage />);

    // Select Java
    const select = screen.getByLabelText('Programming Language');
    fireEvent.change(select, { target: { value: 'java' } });

    // Enter code
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: 'public class Main { public static void main(String[] args) {} }' } });

    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    fireEvent.click(submitBtn);

    expect(spy).toHaveBeenCalledWith({
      code: 'public class Main { public static void main(String[] args) {} }',
      language: 'java',
      context: null,
    });

    expect(await screen.findByText('Java code review completed.')).toBeInTheDocument();
  });

  it('handles backend service unavailable error (503)', async () => {
    vi.spyOn(apiClient, 'submitReview').mockRejectedValueOnce(
      new ApiError(503, 'SERVICE_UNAVAILABLE', 'Gemini API quota exceeded. Please try again shortly.')
    );

    render(<WorkspacePage />);
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: 'def foo(): pass' } });

    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    fireEvent.click(submitBtn);

    expect(await screen.findByText(/Service Temporarily Unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/Gemini API quota exceeded/i)).toBeInTheDocument();
  });

  it('handles network connection error', async () => {
    vi.spyOn(apiClient, 'submitReview').mockRejectedValueOnce(
      new ApiError(0, 'NETWORK_ERROR', 'Unable to connect to CodeSage backend at http://localhost:8000.')
    );

    render(<WorkspacePage />);
    const textarea = screen.getByLabelText('Python code input');
    fireEvent.change(textarea, { target: { value: 'def foo(): pass' } });

    const submitBtn = screen.getByRole('button', { name: /Run Code Review/i });
    fireEvent.click(submitBtn);

    expect(await screen.findByText(/Network Connection Failure/i)).toBeInTheDocument();
    expect(screen.getByText(/Unable to connect to CodeSage backend/i)).toBeInTheDocument();
  });
});
