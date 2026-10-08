import { spawn } from 'node:child_process';
import { appendFile, mkdir, open, readFile, rm, writeFile } from 'node:fs/promises';
import { readFileSync, unlinkSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { changedFiles, checkContract, endingPatch, formattingRepairs, snapshot } from './pwa-guard-core.mjs';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = join(frontend, 'test-results/pwa-guard');
const args = new Set(process.argv.slice(2));
if ([...args].some((arg) => !['--static', '--watch', '--fix'].includes(arg))) {
  console.error('Usage: node scripts/pwa-guard.mjs [--static] [--watch] [--fix]');
  process.exit(2);
}
let stopping = false;
let child;
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => {
  stopping = true;
  if (child?.pid) {
    try {
      if (process.platform === 'win32') child.kill('SIGTERM');
      else process.kill(-child.pid, 'SIGTERM');
    } catch (error) { if (error.code !== 'ESRCH') console.error(error.message); }
  }
});

async function phase(name, executable, argv) {
  console.log(`\n[pwa-guard] ${name}`);
  const started = Date.now();
  const log = [`\n--- ${name} ---\n`];
  const code = await new Promise((resolveCode) => {
    child = spawn(executable, argv, {
      cwd: frontend, detached: process.platform !== 'win32',
      env: { ...process.env, ASTRO_TELEMETRY_DISABLED: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    child.stdout.on('data', (data) => { process.stdout.write(data); log.push(data.toString()); });
    child.stderr.on('data', (data) => { process.stderr.write(data); log.push(data.toString()); });
    child.once('error', (error) => { log.push(error.message); console.error(error.message); resolveCode(1); });
    child.once('close', (status) => { child = undefined; resolveCode(status ?? 1); });
  });
  await appendFile(join(output, 'guard.log'), log.join(''));
  return { name, passed: code === 0, exitCode: code, milliseconds: Date.now() - started };
}

async function report(result) {
  result.passed = result.findings.length === 0 && result.phases.every((item) => item.passed) && !stopping;
  result.finishedAt = new Date().toISOString();
  await writeFile(join(output, 'report.json'), JSON.stringify(result, null, 2) + '\n');
  const lines = [
    `# PWA compatibility: ${result.passed ? 'PASS' : 'FAIL'}`, '',
    `Mode: ${result.mode}. Finished: ${result.finishedAt}.`, '',
    ...result.phases.map((item) => `- ${item.passed ? 'PASS' : 'FAIL'}: ${item.name} (${item.milliseconds} ms)`),
    ...result.findings.map((item) => `- ${item.file ?? 'Guard'}${item.line ? `:${item.line}` : ''}: ${item.message}`),
    '',
    'On a failure: inspect guard.log and browser-results.json/traces, compare the shared contract in docs/pwa-offline-queue.md, and coordinate semantic changes with Team 3.',
    'Any formatting.patch only normalizes EOF whitespace in the four queue integration files. Review it before applying. The checker does not rewrite payloads, replay logic, or domain types.',
    'Static-only mode does not establish runtime correctness. A passing run covers the current checkout and defined scenarios, not unseen branches or every possible regression.', '',
  ];
  await writeFile(join(output, 'report.md'), lines.join('\n'));
  if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY, lines.join('\n') + '\n');
  console.log(`\n[pwa-guard] ${result.passed ? 'PASS' : 'FAIL'} — test-results/pwa-guard/report.md`);
  return result.passed;
}

async function run() {
  await mkdir(output, { recursive: true });
  for (const file of ['formatting.patch', 'browser-results.json']) await rm(join(output, file), { force: true });
  await rm(join(frontend, 'test-results/pwa-browser'), { recursive: true, force: true });
  await writeFile(join(output, 'guard.log'), '');
  const result = { mode: args.has('--static') ? 'static only' : 'contract + built browser integration', phases: [], findings: [] };
  await writeFile(join(output, 'report.json'), JSON.stringify({ status: 'running', startedAt: new Date().toISOString(), mode: result.mode }, null, 2) + '\n');
  await writeFile(join(output, 'report.md'), '# PWA compatibility: RUNNING\n\nThe previous result is no longer current.\n');
  let checkedSnapshot;
  try {
    const repairs = await formattingRepairs(frontend);
    if (repairs.length) {
      await writeFile(join(output, 'formatting.patch'), repairs.map(endingPatch).join(''));
      for (const repair of repairs) {
        if (args.has('--fix')) {
          // Refuse to overwrite a file that changed since the proposal was made.
          if (await readFile(join(frontend, repair.file), 'utf8') !== repair.before) throw new Error(`${repair.file} changed during repair; rerun the checker`);
          await writeFile(join(frontend, repair.file), repair.after);
          console.log(`[pwa-guard] normalized EOF: ${repair.file}`);
        } else result.findings.push({ file: repair.file, message: 'Normalize EOF whitespace; review formatting.patch or run npm run pwa:fix.' });
      }
    }
    checkedSnapshot = await snapshot(frontend);
    const started = Date.now();
    const diagnostics = checkContract(frontend);
    result.findings.push(...diagnostics);
    result.phases.push({ name: 'Team 3 caller contract', passed: diagnostics.length === 0, milliseconds: Date.now() - started });
    for (const finding of result.findings) console.error(`[pwa-guard] ${finding.file ?? 'Guard'}${finding.line ? `:${finding.line}` : ''}: ${finding.message}`);
    if (!result.findings.length && !args.has('--static')) {
      const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
      const commands = [
        ['Guard regression checks', process.execPath, ['--test', 'scripts/pwa-guard.node-test.mjs']],
        ['Astro diagnostics', npm, ['run', 'check']],
        ['Frontend TypeScript', process.execPath, ['node_modules/typescript/bin/tsc', '--noEmit']],
        ['Production build', npm, ['run', 'build']],
        ['Queue browser integration', process.execPath, ['node_modules/@playwright/test/cli.js', 'test', '--config', 'playwright.pwa.config.ts', '--project', 'chromium']],
      ];
      for (const [name, executable, argv] of commands) {
        if (stopping) break;
        const outcome = await phase(name, executable, argv);
        result.phases.push(outcome);
        if (!outcome.passed) break;
      }
    }
  } catch (error) {
    result.findings.push({ message: error.message });
    console.error(`[pwa-guard] ${error.message}`);
  }
  if (checkedSnapshot) {
    const changed = changedFiles(checkedSnapshot, await snapshot(frontend));
    if (changed.length) result.findings.push({ message: `Source changed during verification (${changed.join(', ')}); rerun before trusting this result. Watch mode will rerun automatically.` });
  }
  return report(result);
}

// Poll hashes rather than filesystem events: atomic editor saves and branch
// checkouts are detected, with one run at a time and a rerun for mid-run edits.
await mkdir(output, { recursive: true });
const lockPath = join(output, '.running.lock');
async function acquireLock() {
  try {
    const lock = await open(lockPath, 'wx');
    await lock.writeFile(String(process.pid));
    await lock.close();
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const pid = Number(await readFile(lockPath, 'utf8'));
    if (pid > 0) {
      try { process.kill(pid, 0); }
      catch (checkError) {
        if (checkError.code === 'ESRCH') { await rm(lockPath); return acquireLock(); }
      }
    }
    throw new Error('Another PWA guard owns these reports. Stop it first; if its lock is stale, remove test-results/pwa-guard/.running.lock.');
  }
}
try { await acquireLock(); }
catch (error) { console.error(`[pwa-guard] ${error.message}`); process.exit(2); }
process.once('exit', () => {
  try { if (Number(readFileSync(lockPath, 'utf8')) === process.pid) unlinkSync(lockPath); }
  catch { /* A missing lock does not change the completed check result. */ }
});
let previous = await snapshot(frontend);
let passed = await run();
while (args.has('--watch') && !stopping) {
  await new Promise((resolveWait) => setTimeout(resolveWait, 1000));
  if (stopping) break;
  const current = await snapshot(frontend);
  const changed = changedFiles(previous, current);
  if (!changed.length) continue;
  await new Promise((resolveWait) => setTimeout(resolveWait, 500));
  previous = await snapshot(frontend);
  console.log(`\n[pwa-guard] changes detected:\n${changed.map((file) => `  ${file}`).join('\n')}`);
  passed = await run();
}
process.exitCode = stopping ? 130 : passed ? 0 : 1;
