import React, { useState } from 'react';

interface Props {
  quoteId: string;
  initiallySaved?: boolean;
}

export default function FavoriteButton({ quoteId, initiallySaved = false }: Props) {
  const [saved, setSaved] = useState(initiallySaved);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function toggle() {
    setBusy(true);
    setError('');
    try {
      const response = await fetch(saved ? `/api/v1/favorites/${encodeURIComponent(quoteId)}` : '/api/v1/favorites', {
        method: saved ? 'DELETE' : 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: saved ? undefined : JSON.stringify({ quoteId }),
      });
      if (!response.ok) throw new Error(`Favorite request failed (${response.status})`);
      setSaved(!saved);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not update favorite');
    } finally {
      setBusy(false);
    }
  }

  return (
    <span>
      <button type="button" onClick={() => void toggle()} disabled={busy} aria-pressed={saved}>
        {busy ? 'Saving…' : saved ? 'Remove from library' : 'Save to library'}
      </button>
      {error ? <span role="alert"> {error}</span> : null}
    </span>
  );
}
