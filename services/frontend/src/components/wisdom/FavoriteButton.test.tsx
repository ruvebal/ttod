// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import FavoriteButton from './FavoriteButton';

describe('FavoriteButton', () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it('saves and then removes a quote', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 201 }))
      .mockResolvedValueOnce(new Response('{}', { status: 200 }));
    render(<FavoriteButton quoteId="wis-001" />);

    fireEvent.click(screen.getByRole('button', { name: 'Save to library' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Remove from library' })).toBeInTheDocument());
    expect(fetchMock).toHaveBeenNthCalledWith(1, '/api/v1/favorites', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ quoteId: 'wis-001' }),
    }));

    fireEvent.click(screen.getByRole('button', { name: 'Remove from library' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Save to library' })).toBeInTheDocument());
    expect(fetchMock).toHaveBeenNthCalledWith(2, '/api/v1/favorites/wis-001', expect.objectContaining({ method: 'DELETE' }));
  });
});
