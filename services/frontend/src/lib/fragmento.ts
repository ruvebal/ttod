/** El id que pide el fragmento, o `''` si no hay o está mal formado (`#%E0%A4%A` no rompe nada). */
export function idDelFragmento(hash: string): string {
  try {
    return decodeURIComponent(hash.replace(/^#/, ''));
  } catch {
    return '';
  }
}
