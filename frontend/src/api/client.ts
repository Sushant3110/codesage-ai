/**
 * Typed API Client for CodeSage AI Backend
 */

import type {
  CapabilitiesResponse,
  HealthResponse,
  PaginatedResponse,
  ReadinessResponse,
  ReviewRequest,
  ReviewResponse,
  ReviewSummary,
} from '../types/review';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;
  code: string;
  detail: string;

  constructor(status: number, code: string, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});
  
  if (options.body && typeof options.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response: Response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : 'Failed to connect';
    throw new ApiError(
      0,
      'NETWORK_ERROR',
      `Unable to connect to CodeSage backend at ${BASE_URL}. Ensure the FastAPI server is running. (${errorMsg})`
    );
  }

  if (!response.ok) {
    let code = 'UNKNOWN_ERROR';
    let detail = `Server returned status ${response.status} (${response.statusText})`;

    try {
      const data = await response.json();
      if (typeof data.detail === 'string') {
        detail = data.detail;
      } else if (Array.isArray(data.detail)) {
        // FastAPI 422 validation array
        detail = data.detail.map((d: { msg?: string; loc?: string[] }) => d.msg || JSON.stringify(d)).join('; ');
      } else if (typeof data.detail === 'object' && data.detail !== null) {
        detail = data.detail.detail || JSON.stringify(data.detail);
        if (data.detail.code) code = data.detail.code;
      }
      if (data.code) {
        code = data.code;
      }
    } catch {
      // Non-JSON response
    }

    if (response.status === 413) code = 'PAYLOAD_TOO_LARGE';
    if (response.status === 422 && code === 'UNKNOWN_ERROR') code = 'VALIDATION_ERROR';
    if (response.status === 503 && code === 'UNKNOWN_ERROR') code = 'SERVICE_UNAVAILABLE';
    if (response.status === 404 && code === 'UNKNOWN_ERROR') code = 'NOT_FOUND';

    throw new ApiError(response.status, code, detail);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  getHealth: () => request<HealthResponse>('/api/v1/health'),
  
  getReadiness: () => request<ReadinessResponse>('/api/v1/ready'),
  
  getCapabilities: () => request<CapabilitiesResponse>('/api/v1/capabilities'),
  
  submitReview: (req: ReviewRequest) =>
    request<ReviewResponse>('/api/v1/reviews', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
    
  getReview: (id: string) => request<ReviewResponse>(`/api/v1/reviews/${encodeURIComponent(id)}`),
  
  getHistory: (page = 1, pageSize = 20) =>
    request<PaginatedResponse<ReviewSummary>>(
      `/api/v1/history?page=${encodeURIComponent(page)}&page_size=${encodeURIComponent(pageSize)}`
    ),
};
