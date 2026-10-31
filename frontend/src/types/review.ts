/**
 * CodeSage AI — TypeScript Data Contracts
 * Mirroring backend Pydantic models in app/schemas/
 */

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';

export type Category =
  | 'security'
  | 'correctness'
  | 'performance'
  | 'maintainability'
  | 'style'
  | 'documentation';

export type FindingSource = 'llm' | 'ruff' | 'bandit';

export type VerificationStatus = 'deterministic' | 'unverified';

export interface LineRange {
  start: number;
  end: number;
}

export interface Patch {
  original: string;
  suggested: string;
}

export interface Citation {
  document_title: string;
  chunk_text: string;
  source_file: string;
  relevance_score: number;
  source_url?: string | null;
  section?: string | null;
}

export interface Finding {
  id: string;
  source: FindingSource;
  severity: Severity;
  category: Category;
  rule_id: string | null;
  title: string;
  explanation: string;
  evidence: string | null;
  line_range: LineRange | null;
  patch: Patch | null;
  citations: Citation[];
  verification_status: VerificationStatus;
}

export type SupportedLanguage =
  | 'python'
  | 'java'
  | 'javascript'
  | 'typescript'
  | 'c'
  | 'cpp'
  | 'html'
  | 'css'
  | 'sql';

export interface ReviewRequest {
  code: string;
  language: SupportedLanguage;
  context?: string | null;
}

export interface FindingCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface ReviewResponse {
  id: string;
  submitted_at: string;
  code_hash: string;
  language: string;
  summary: string;
  findings: Finding[];
  static_analysis_ran: boolean;
  rag_context_retrieved: boolean;
  finding_counts: FindingCounts;
}

export interface ReviewSummary {
  id: string;
  submitted_at: string;
  code_snippet: string;
  finding_counts: FindingCounts;
  language: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CapabilitiesResponse {
  supported_languages: string[];
  llm_model: string;
  static_analysis_tools: string[];
  rag_enabled: boolean;
  rag_document_count: number;
  max_code_size_bytes: number;
}

export interface HealthResponse {
  status: 'ok';
  version: string;
}

export interface ReadinessResponse {
  status: 'ready' | 'not_ready';
  checks: {
    mongodb: string;
    chromadb: string;
  };
}

export interface ApiErrorDetail {
  detail: string;
  code: string;
}
