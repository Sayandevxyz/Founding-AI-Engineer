/**
 * Replicate.AI Test Suite Runner
 */
const { spawnSync } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const pythonExe = process.platform === 'win32'
  ? path.join(rootDir, 'backend', 'venv', 'Scripts', 'python.exe')
  : path.join(rootDir, 'backend', 'venv', 'bin', 'python');

console.log('\x1b[36m%s\x1b[0m', 'Running Replicate.AI automated tests (Backend + Unit + Integration)...');

const result = spawnSync(`"${pythonExe}"`, ['-m', 'pytest', 'backend/tests/test_backend.py', '-v'], {
  cwd: rootDir,
  shell: true,
  stdio: 'inherit',
  env: { ...process.env, PYTHONPATH: rootDir }
});

if (result.status === 0) {
  console.log('\x1b[32m%s\x1b[0m', '\nAll automated tests passed successfully!');
  process.exit(0);
} else {
  console.error('\x1b[31m%s\x1b[0m', '\nTests failed.');
  process.exit(result.status || 1);
}
