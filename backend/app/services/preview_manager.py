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

    def is_port_listening(self, port: int) -> bool:
        """Check if port is currently open and accepting connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            res = s.connect_ex(("127.0.0.1", port))
            return res == 0

    async def is_server_healthy(self, port: int) -> bool:
        """Verify that server responds to HTTP requests."""
        if not self.is_port_listening(port):
            return False
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"http://127.0.0.1:{port}")
                return res.status_code in [200, 304, 404]
        except Exception:
            return False

    def get_free_port(self) -> int:
        """Find an available TCP port starting from base_port."""
        for port in range(self.base_port, self.max_port):
            if port in self.allocated_ports.values():
                continue
            if not self.is_port_listening(port):
                return port
        return 3001

    def ensure_node_modules(self, project_dir: str):
        """Ensure node_modules is present, linking from template cache if needed."""
        nm = os.path.join(project_dir, "node_modules")
        if not os.path.exists(nm):
            projects_root = os.path.abspath(os.path.join("generated", "projects"))
            candidates = [
                os.path.abspath(os.path.join("generated", "projects", "test-e2e", "node_modules"))
            ]
            if os.path.exists(projects_root):
                for p in os.listdir(projects_root):
                    c = os.path.join(projects_root, p, "node_modules")
                    if os.path.exists(c) and os.path.abspath(c) != os.path.abspath(nm):
                        candidates.append(c)
            for candidate in candidates:
                if os.path.exists(candidate) and os.path.abspath(candidate) != os.path.abspath(nm):
                    try:
                        subprocess.run(["cmd", "/c", "mklink", "/J", nm, candidate], capture_output=True)
                        if os.path.exists(nm):
                            break
                    except Exception:
                        pass

    async def start_preview(self, project_id: str, project_dir: str, target_port: Optional[int] = None) -> int:
        """Launch local preview server for the specified generated project."""
        await self.stop_preview(project_id)

        self.ensure_node_modules(project_dir)

        # Ensure dist exists
        dist_dir = os.path.join(project_dir, "dist")
        if not os.path.exists(dist_dir) or not os.path.exists(os.path.join(dist_dir, "index.html")):
            try:
                proc = await asyncio.create_subprocess_shell(
                    "npx vite build",
                    cwd=project_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await asyncio.wait_for(proc.communicate(), timeout=30.0)
            except Exception:
                pass

        port = target_port if target_port and not self.is_port_listening(target_port) else self.get_free_port()
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
        return port

    async def ensure_preview_running(self, project_id: str, project_dir: str, preferred_port: Optional[int] = None) -> int:
        """Guarantee preview server is alive and responding."""
        if preferred_port and await self.is_server_healthy(preferred_port):
            self.allocated_ports[project_id] = preferred_port
            return preferred_port

        # If process in tracking is dead or not healthy, restart it
        return await self.start_preview(project_id, project_dir, target_port=preferred_port)

    async def stop_preview(self, project_id: str):
        """Safely terminate any running preview process for this project."""
        proc = self.running_processes.pop(project_id, None)
        port = self.allocated_ports.pop(project_id, None)
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
                    if res.status_code in [200, 304]:
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
