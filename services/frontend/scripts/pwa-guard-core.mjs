import { createHash } from 'node:crypto';
import { readdir, readFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import ts from 'typescript';

export const repairableFiles = [
  'src/lib/db.ts',
  'src/types/domain.ts',
  'src/components/oracle/OracleTerminal.tsx',
  'public/sw.js',
];

export function checkContract(frontend, replacements = new Map()) {
  const options = {
    strict: true, noEmit: true, skipLibCheck: true, types: [],
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    lib: ['lib.es2022.d.ts', 'lib.dom.d.ts'],
  };
  const host = ts.createCompilerHost(options);
  const originalRead = host.readFile.bind(host);
  host.readFile = (file) => replacements.get(file) ?? originalRead(file);
  const program = ts.createProgram([join(frontend, 'contracts/pwa-queue.ts')], options, host);
  return ts.getPreEmitDiagnostics(program).map((diagnostic) => {
    const location = diagnostic.file && diagnostic.start !== undefined
      ? diagnostic.file.getLineAndCharacterOfPosition(diagnostic.start) : undefined;
    return {
      file: diagnostic.file ? relative(frontend, diagnostic.file.fileName) : undefined,
      line: location ? location.line + 1 : undefined,
      message: ts.flattenDiagnosticMessageText(diagnostic.messageText, '\n'),
    };
  });
}

export function normalizeEnding(file, source) {
  // Never touch malformed source or whitespace inside literals/JSX. Only the
  // suffix after a syntactically complete file can be normalized automatically.
  const parsed = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true);
  if (parsed.parseDiagnostics.length) return source;
  return source.trimEnd() + '\n';
}

export async function formattingRepairs(frontend) {
  const repairs = [];
  for (const file of repairableFiles) {
    const before = await readFile(join(frontend, file), 'utf8');
    const after = normalizeEnding(file, before);
    if (before !== after) repairs.push({ file, before, after });
  }
  return repairs;
}

export function endingPatch({ file, before, after }) {
  const lines = (text) => {
    const result = text.split('\n');
    if (result.at(-1) === '') result.pop();
    return result;
  };
  const oldLines = lines(before);
  const newLines = lines(after);
  let common = 0;
  while (common < Math.min(oldLines.length, newLines.length) && oldLines[common] === newLines[common]) common++;
  // A missing final newline changes even an otherwise identical last line.
  if (!before.endsWith('\n') && common === oldLines.length) common = Math.max(0, common - 1);
  const start = Math.max(0, common - 3);
  const path = `services/frontend/${file}`;
  const patch = [`diff --git a/${path} b/${path}`, `--- a/${path}`, `+++ b/${path}`,
    `@@ -${oldLines.length ? start + 1 : 0},${oldLines.length - start} +${newLines.length ? start + 1 : 0},${newLines.length - start} @@`];
  for (let index = start; index < common; index++) patch.push(` ${oldLines[index]}`);
  for (let index = common; index < oldLines.length; index++) {
    patch.push(`-${oldLines[index]}`);
    if (index === oldLines.length - 1 && !before.endsWith('\n')) patch.push('\\ No newline at end of file');
  }
  for (let index = common; index < newLines.length; index++) patch.push(`+${newLines[index]}`);
  return patch.join('\n') + '\n';
}

export async function snapshot(frontend) {
  const files = new Map();
  const roots = ['src', 'public', 'contracts', 'e2e', 'scripts', 'package.json', 'package-lock.json',
    'tsconfig.json', 'astro.config.mjs', 'playwright.config.ts', 'playwright.pwa.config.ts',
    '../../.github/workflows/ci.yml', '../../docs/pwa-offline-queue.md', '../../docs/pwa-compatibility-monitor.md'];
  async function visit(path) {
    try {
      const entries = await readdir(path, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory() && !['node_modules', 'dist', '.astro', 'test-results'].includes(entry.name)) await visit(join(path, entry.name));
        else if (entry.isFile()) await hash(join(path, entry.name));
      }
    } catch (error) {
      if (error.code === 'ENOTDIR') await hash(path);
      else if (error.code !== 'ENOENT') throw error;
    }
  }
  async function hash(path) {
    try {
      files.set(relative(frontend, path), createHash('sha256').update(await readFile(path)).digest('hex'));
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  for (const root of roots) await visit(join(frontend, root));
  return files;
}

export function changedFiles(before, after) {
  return [...new Set([...before.keys(), ...after.keys()])]
    .filter((file) => before.get(file) !== after.get(file)).sort();
}
