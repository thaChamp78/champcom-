"""
ChampCom Process Manager - Real subprocess control and sandboxing
Manages child processes with monitoring, output capture, and cleanup.
"""
import subprocess
import threading
import os
import signal
import time
from collections import deque


class ManagedProcess:
    """A real managed subprocess with output capture."""

    def __init__(self, name, command, cwd=None, env=None):
        self.name = name
        self.command = command
        self.cwd = cwd or os.getcwd()
        self.env = env
        self.process = None
        self.stdout_lines = deque(maxlen=1000)
        self.stderr_lines = deque(maxlen=1000)
        self.return_code = None
        self.start_time = None
        self.end_time = None
        self.on_output = None  # callback(line, is_stderr)
        self.on_exit = None  # callback(return_code)

    def start(self):
        """Launch the subprocess."""
        self.start_time = time.time()
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=isinstance(self.command, str),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
                preexec_fn=os.setsid if os.name != 'nt' else None,
            )
            # Start output readers
            threading.Thread(target=self._read_stdout, daemon=True).start()
            threading.Thread(target=self._read_stderr, daemon=True).start()
            threading.Thread(target=self._wait, daemon=True).start()
            return True
        except Exception as e:
            self.stderr_lines.append(f"Failed to start: {e}")
            return False

    def _read_stdout(self):
        for line in iter(self.process.stdout.readline, b''):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            self.stdout_lines.append(decoded)
            if self.on_output:
                self.on_output(decoded, False)

    def _read_stderr(self):
        for line in iter(self.process.stderr.readline, b''):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            self.stderr_lines.append(decoded)
            if self.on_output:
                self.on_output(decoded, True)

    def _wait(self):
        self.process.wait()
        self.return_code = self.process.returncode
        self.end_time = time.time()
        if self.on_exit:
            self.on_exit(self.return_code)

    def stop(self, timeout=5):
        """Gracefully stop the process, force kill if needed."""
        if not self.process or self.process.poll() is not None:
            return

        try:
            if os.name != 'nt':
                # Send SIGTERM to process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            else:
                self.process.terminate()

            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                if os.name != 'nt':
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                else:
                    self.process.kill()
                self.process.wait()
        except (ProcessLookupError, OSError):
            pass

        self.return_code = self.process.returncode
        self.end_time = time.time()

    @property
    def alive(self):
        return self.process and self.process.poll() is None

    @property
    def pid(self):
        return self.process.pid if self.process else None

    @property
    def runtime(self):
        if self.start_time:
            end = self.end_time or time.time()
            return end - self.start_time
        return 0

    def get_info(self):
        return {
            "name": self.name,
            "pid": self.pid,
            "alive": self.alive,
            "return_code": self.return_code,
            "runtime": round(self.runtime, 1),
            "stdout_lines": len(self.stdout_lines),
            "stderr_lines": len(self.stderr_lines),
        }


class ProcessManager:
    """Manages multiple subprocesses with lifecycle control."""

    def __init__(self):
        self.processes = {}  # name -> ManagedProcess
        self.lock = threading.Lock()

    def launch(self, name, command, cwd=None, env=None,
               on_output=None, on_exit=None):
        """Launch a new managed process."""
        with self.lock:
            # Stop existing process with same name
            if name in self.processes and self.processes[name].alive:
                self.processes[name].stop()

            proc = ManagedProcess(name, command, cwd, env)
            proc.on_output = on_output
            proc.on_exit = on_exit
            self.processes[name] = proc

            if proc.start():
                return proc
            return None

    def stop(self, name, timeout=5):
        """Stop a process by name."""
        with self.lock:
            if name in self.processes:
                self.processes[name].stop(timeout)
                return True
        return False

    def stop_all(self, timeout=5):
        """Stop all running processes."""
        with self.lock:
            for proc in self.processes.values():
                if proc.alive:
                    proc.stop(timeout)

    def get(self, name):
        return self.processes.get(name)

    def list_running(self):
        return [
            proc.get_info()
            for proc in self.processes.values()
            if proc.alive
        ]

    def list_all(self):
        return [proc.get_info() for proc in self.processes.values()]

    def cleanup_dead(self):
        """Remove completed processes from tracking."""
        with self.lock:
            dead = [n for n, p in self.processes.items() if not p.alive]
            for name in dead:
                del self.processes[name]
            return len(dead)
