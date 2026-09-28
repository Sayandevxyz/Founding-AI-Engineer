/**
 * Replicate.AI Unified Local Development Orchestrator
 * Launches both FastAPI agent backend (Port 8000) and Next.js Control Panel (Port 3000).
 */
const { spawn } = require('child_process');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const pythonExe = process.platform === 'win32'
  ? path.join(rootDir, 'backend', 'venv', 'Scripts', 'python.exe')
  : path.join(rootDir, 'backend', 'venv', 'bin', 'python');

console.log('\x1b[36m%s\x1b[0m', '=====================================================');
console.log('\x1b[36m%s\x1b[0m', '   REPLICATE.AI — Autonomous Reconstruction Agent   ');
console.log('\x1b[36m%s\x1b[0m', '=====================================================');
console.log('\x1b[32m%s\x1b[0m', '[1/2] Starting FastAPI Agent Orchestration Backend on http://127.0.0.1:8000 ...');

const backend = spawn(`"${pythonExe}"`, ['-m', 'uvicorn', 'backend.app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'], {
  cwd: rootDir,
  shell: true,
  stdio: 'inherit',
  env: { ...process.env, PYTHONPATH: rootDir }
});

console.log('\x1b[34m%s\x1b[0m', '[2/2] Starting Next.js Control Dashboard on http://localhost:3000 ...');

const frontend = spawn('npm', ['run', 'dev'], {
  cwd: path.join(rootDir, 'apps', 'dashboard'),
  shell: true,
  stdio: 'inherit',
  env: process.env
});

function cleanup() {
  console.log('\n\x1b[33m%s\x1b[0m', 'Shutting down Replicate.AI services...');
  if (process.platform === 'win32') {
    if (backend.pid) spawn('taskkill', ['/F', '/T', '/PID', backend.pid.toString()], { shell: true });
    if (frontend.pid) spawn('taskkill', ['/F', '/T', '/PID', frontend.pid.toString()], { shell: true });
  } else {
    backend.kill();
    frontend.kill();
  }
  process.exit(0);
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
