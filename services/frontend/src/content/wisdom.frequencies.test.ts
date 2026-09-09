import { describe, expect, it } from 'vitest';

import type { WisdomEntry } from '../types/domain';
import { frequencies } from './wisdom';

function fixture(partial: Pick<WisdomEntry, 'id' | 'section' | 'level' | 'tags'>): WisdomEntry {
  return {
    text: 'disposable fixture — not loaded from ttod.yml',
    teaches: 'unit-test only',
    related: [],
    origin: 'human',
    lang: 'en',
    rights: { license: 'CC-BY-NC-SA-4.0' },
    ...partial,
  };
}

describe('frequencies()', () => {
  it('counts sections, levels, and flattened tags, then sorts keys alphabetically', () => {
    const entries = [
      fixture({ id: 'fix-001', section: 'wisdom', level: 'beginner', tags: ['focus', 'clarity'] }),
      fixture({ id: 'fix-002', section: 'wisdom', level: 'advanced', tags: ['focus'] }),
      fixture({ id: 'fix-003', section: 'architecture', level: 'beginner', tags: [] }),
    ];

    expect(frequencies(entries, 'section')).toEqual([
      ['architecture', 1],
      ['wisdom', 2],
    ]);
    expect(frequencies(entries, 'level')).toEqual([
      ['advanced', 1],
      ['beginner', 2],
    ]);
    expect(frequencies(entries, 'tags')).toEqual([
      ['clarity', 1],
      ['focus', 2],
    ]);
  });
});
