import type { WisdomEntry } from '../../types/domain';

// A corpus small enough to read, shaped like the real one: each locale has its own ids, joined by
// one-way `translation_of` edges (es → en), English tag keys in both, and the registry's values
// (section architecture, level advanced, tag koan, search words diseno / simplicity).
const q = (id: string, lang: 'en' | 'es', section: string, level: WisdomEntry['level'], tags: string[], text: string): WisdomEntry => ({
  id, lang, section, level, tags, text, teaches: `Teaches ${id}`, related: [], origin: 'human',
  rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
});

export const corpus: WisdomEntry[] = [
  q('wis-034', 'es', 'wisdom', 'beginner', ['koan'], 'El diseño es la deuda que se paga antes.'),
  q('arch-060', 'es', 'architecture', 'advanced', ['koan', 'debt'], 'Un límite sin pruebas es un deseo.'),
  q('arch-061', 'es', 'architecture', 'beginner', ['design'], 'Nombra la frontera antes de cruzarla.'),
  q('wis-033', 'en', 'wisdom', 'beginner', ['koan'], 'Simplicity is design paid in advance.'),
  q('arch-008', 'en', 'architecture', 'advanced', ['koan', 'debt'], 'A boundary without tests is a wish.'),
  q('arch-052', 'en', 'architecture', 'beginner', ['design'], 'Name the border before you cross it.'),
];

export const edges = [
  { source: 'wis-034', target: 'wis-033', rel: 'translation_of' },
  { source: 'arch-060', target: 'arch-008', rel: 'translation_of' },
  { source: 'arch-061', target: 'arch-052', rel: 'translation_of' },
  { source: 'arch-060', target: 'arch-061', rel: 'related' },
];
