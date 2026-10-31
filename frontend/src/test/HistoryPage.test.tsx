import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { HistoryPage } from '../pages/HistoryPage';
import { apiClient, ApiError } from '../api/client';
import type { PaginatedResponse, ReviewSummary } from '../types/review';

const mockHistoryResponse: PaginatedResponse<ReviewSummary> = {
  items: [
    {
      id: 'rev-uuid-1',
      submitted_at: '2026-10-30T10:00:00Z',
      code_snippet: 'def ping(ip):\n    os.system(ip)',
      finding_counts: { critical: 0, high: 1, medium: 0, low: 0, info: 0 },
      language: 'python',
    },
    {
      id: 'rev-uuid-2',
      submitted_at: '2026-10-30T11:00:00Z',
      code_snippet: 'def clean():\n    return 42',
      finding_counts: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
      language: 'python',
    },
  ],
  total: 25,
  page: 1,
  page_size: 10,
  total_pages: 3,
};

describe('HistoryPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches and renders paginated review items', async () => {
    vi.spyOn(apiClient, 'getHistory').mockResolvedValueOnce(mockHistoryResponse);

    render(
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    );

    expect((await screen.findAllByText(/rev-uuid/)).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/def ping\(ip\)/)).toBeInTheDocument();
    expect(screen.getByText(/Showing page/)).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // total_pages
  });

  it('triggers page change on Next click', async () => {
    const spy = vi.spyOn(apiClient, 'getHistory').mockResolvedValue(mockHistoryResponse);

    render(
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    );

    const nextBtn = await screen.findByRole('button', { name: /Next/i });
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith(2, 10);
    });
  });

  it('handles empty review history', async () => {
    vi.spyOn(apiClient, 'getHistory').mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 0,
    });

    render(
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    );

    expect(await screen.findByText(/No Review History Found/i)).toBeInTheDocument();
  });

  it('handles backend error when fetching history', async () => {
    vi.spyOn(apiClient, 'getHistory').mockRejectedValueOnce(
      new ApiError(503, 'SERVICE_UNAVAILABLE', 'MongoDB is not accessible.')
    );

    render(
      <MemoryRouter>
        <HistoryPage />
      </MemoryRouter>
    );

    expect(await screen.findByText(/Failed to Load History/i)).toBeInTheDocument();
    expect(screen.getByText(/MongoDB is not accessible/i)).toBeInTheDocument();
  });
});
