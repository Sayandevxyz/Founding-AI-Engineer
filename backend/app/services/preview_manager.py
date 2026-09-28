"""Preview Manager: Allocates dynamic ports and lifecycle manages local generated preview servers."""
import os
import socket
import asyncio
import subprocess
import httpx
from typing import Dict, Optional


class PreviewManager:
    def __init__(self, base_port: int = 3001, max_port: int = 3999):
        self.base_port = base_port
        self.max_port = max_port
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.allocated_ports: Dict[str, int] = {}

    def get_free_port(self) -> int:
        """Find an available TCP port starting from base_port."""
        for port in range(self.base_port, self.max_port):
            if port in self.allocated_ports.values():
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                res = s.connect_ex(("127.0.0.1", port))
                if res != 0:  # Port is free
                    return port
        return 3001

    async def start_preview(self, project_id: str, project_dir: str) -> int:
        """Launch local preview server for the specified generated project."""
        await self.stop_preview(project_id)

        port = self.get_free_port()
        self.allocated_ports[project_id] = port

        # Start vite preview server
        cmd = f"npx vite preview --port {port} --host 0.0.0.0"
        proc = subprocess.Popen(
            cmd,
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        self.running_processes[project_id] = proc

        # Wait for port readiness
        ready = await self._wait_for_ready(port, timeout_secs=10.0)
        if not ready:
            # Proc might still be alive or started quickly
            pass

        return port

    async def stop_preview(self, project_id: str):
        """Safely terminate any running preview process for this project."""
        proc = self.running_processes.pop(project_id, None)
        self.allocated_ports.pop(project_id, None)
        if proc:
            try:
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    async def _wait_for_ready(self, port: int, timeout_secs: float = 8.0) -> bool:
        start_time = asyncio.get_event_loop().time()
        url = f"http://127.0.0.1:{port}"
        async with httpx.AsyncClient(timeout=1.0) as client:
            while (asyncio.get_event_loop().time() - start_time) < timeout_secs:
                try:
                    res = await client.get(url)
                    if res.status_code == 200:
                        return True
                except Exception:
                    pass
                await asyncio.sleep(0.4)
        return False

    def get_preview_url(self, project_id: str) -> Optional[str]:
        port = self.allocated_ports.get(project_id)
        if port:
            return f"http://localhost:{port}"
        return None
