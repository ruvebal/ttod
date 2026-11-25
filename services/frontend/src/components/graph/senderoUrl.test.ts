import { describe, expect, it } from 'vitest';

import { aliasDeNodos, escribirSendero, leerSendero, validarSendero } from './senderoUrl';

// Nodes carry the related quote's id (the same in /en/ and /es/) and show the locale twin's id.
const alias = aliasDeNodos([
  { id: 'wis-033', idTexto: 'wis-034' },
  { id: 'arch-008', idTexto: 'arch-060' },
  { id: 'arch-052', idTexto: 'arch-061' },
]);

describe('3D graph URL state (?from=&to=&node=)', () => {
  it('reads the three keys', () => {
    expect(leerSendero('?from=wis-034&to=arch-060&node=arch-061&s=x')).toEqual({ from: 'wis-034', to: 'arch-060', node: 'arch-061' });
    expect(leerSendero('')).toEqual({ from: '', to: '', node: '' });
  });
  it('drops ids the graph does not have, and a path to itself', () => {
    expect(validarSendero({ from: 'ghost-1', to: 'arch-008', node: 'nope' }, alias)).toEqual({ from: '', to: 'arch-008', node: '' });
    expect(validarSendero({ from: 'wis-033', to: 'wis-034', node: '' }, alias)).toEqual({ from: 'wis-033', to: '', node: '' });
  });
  it('accepts the shown (locale twin) id and keeps the node id, the same in both locales', () => {
    expect(validarSendero({ from: 'wis-034', to: 'arch-061', node: 'arch-060' }, alias)).toEqual({ from: 'wis-033', to: 'arch-052', node: 'arch-008' });
  });
  it('writes them back, keeping other keys and the hash, removing empty ones', () => {
    expect(escribirSendero('http://x/es/graph/?s=1#a', { from: 'wis-034', to: 'arch-060', node: '' })).toBe('/es/graph/?s=1&from=wis-034&to=arch-060#a');
    expect(escribirSendero('http://x/es/graph/?from=wis-034&node=arch-061', { from: '', to: '', node: '' })).toBe('/es/graph/');
  });
});
