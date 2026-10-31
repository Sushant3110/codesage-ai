import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SeverityBadge, CategoryBadge, SourceBadge, VerificationBadge } from '../components/ui/Badge';
import { PatchDiff } from '../components/review/PatchDiff';
import { CitationBadge } from '../components/review/CitationBadge';
import type { Citation, Patch } from '../types/review';

describe('Badge Components', () => {
  it('renders severity badges correctly', () => {
    const { rerender } = render(<SeverityBadge severity="critical" />);
    expect(screen.getByText('critical')).toBeInTheDocument();

    rerender(<SeverityBadge severity="high" />);
    expect(screen.getByText('high')).toBeInTheDocument();

    rerender(<SeverityBadge severity="medium" />);
    expect(screen.getByText('medium')).toBeInTheDocument();

    rerender(<SeverityBadge severity="low" />);
    expect(screen.getByText('low')).toBeInTheDocument();

    rerender(<SeverityBadge severity="info" />);
    expect(screen.getByText('info')).toBeInTheDocument();
  });

  it('renders category badges correctly', () => {
    render(<CategoryBadge category="security" />);
    expect(screen.getByText('security')).toBeInTheDocument();
  });

  it('renders source badges for LLM and static analysis', () => {
    const { rerender } = render(<SourceBadge source="llm" />);
    expect(screen.getByText('LLM')).toBeInTheDocument();

    rerender(<SourceBadge source="ruff" ruleId="E501" />);
    expect(screen.getByText('RUFF:E501')).toBeInTheDocument();
  });

  it('distinguishes deterministic vs unverified verification status', () => {
    const { rerender } = render(<VerificationBadge status="deterministic" />);
    expect(screen.getByText('Deterministic')).toBeInTheDocument();

    rerender(<VerificationBadge status="unverified" />);
    expect(screen.getByText('Unverified (LLM)')).toBeInTheDocument();
  });
});

describe('PatchDiff Component', () => {
  const samplePatch: Patch = {
    original: 'os.system(f"ping {user_ip}")',
    suggested: 'subprocess.run(["ping", user_ip], shell=False)',
  };

  it('renders original and suggested code', () => {
    render(<PatchDiff patch={samplePatch} />);
    expect(screen.getByText('Suggested Code Patch')).toBeInTheDocument();
    expect(screen.getByText('Original Code')).toBeInTheDocument();
    expect(screen.getByText('Suggested Replacement')).toBeInTheDocument();
    expect(screen.getByText(/os.system/)).toBeInTheDocument();
    expect(screen.getByText(/subprocess.run/)).toBeInTheDocument();
  });

  it('displays safety disclaimer about patches never auto-applied', () => {
    render(<PatchDiff patch={samplePatch} />);
    expect(screen.getByText(/Display-only suggested fix/i)).toBeInTheDocument();
  });
});

describe('CitationBadge Component', () => {
  const sampleCitation: Citation = {
    document_title: 'OWASP Python Security Cheat Sheet',
    section: 'Command Injection',
    chunk_text: 'Never pass unsanitized user input to os.system.',
    source_file: 'owasp_python_security.md',
    source_url: 'https://cheatsheetseries.owasp.org',
    relevance_score: 0.88,
  };

  it('renders document title, section, and percentage match', () => {
    render(<CitationBadge citation={sampleCitation} />);
    expect(screen.getByText('OWASP Python Security Cheat Sheet')).toBeInTheDocument();
    expect(screen.getByText('Command Injection')).toBeInTheDocument();
    expect(screen.getByText('88% match')).toBeInTheDocument();
    expect(screen.getByText(/Source: owasp_python_security.md/)).toBeInTheDocument();
    expect(screen.getByTitle('View authoritative guideline')).toHaveAttribute(
      'href',
      'https://cheatsheetseries.owasp.org'
    );
  });
});
