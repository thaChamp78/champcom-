"""
ChampCom HTTP Server - Real web server backend
Serves the desktop over HTTP so it's accessible from any browser.
Also provides a REST API for all system operations.
Zero external dependencies - uses Python stdlib http.server.
"""
import http.server
import json
import os
import subprocess
import threading
import urllib.parse
import mimetypes
import time


class ChampComAPI:
    """REST API handler for all system operations."""

    def __init__(self, engine):
        self.engine = engine

    def handle(self, method, path, body=None):
        """Route API requests to handlers. Returns (status, response_dict)."""
        routes = {
            "GET": {
                "/api/status": self._status,
                "/api/ecs": self._ecs_info,
                "/api/ai/nodes": self._ai_nodes,
                "/api/config": self._config_get,
                "/api/plugins": self._plugins_list,
                "/api/assets/stats": self._asset_stats,
                "/api/network/stats": self._network_stats,
            },
            "POST": {
                "/api/ai/chat": self._ai_chat,
                "/api/config/set": self._config_set,
                "/api/files/list": self._files_list,
                "/api/files/read": self._files_read,
                "/api/files/write": self._files_write,
                "/api/terminal/exec": self._terminal_exec,
                "/api/ecs/create": self._ecs_create,
            }
        }

        handler = routes.get(method, {}).get(path)
        if handler:
            try:
                return 200, handler(body)
            except Exception as e:
                return 500, {"error": str(e)}
        return 404, {"error": f"Unknown endpoint: {method} {path}"}

    def _status(self, _):
        return {
            "name": "ChampCom",
            "version": self.engine.config.get("app.version", "1.0.0"),
            "uptime": round(self.engine.get_uptime(), 1),
            "ecs_entities": self.engine.ecs.count(),
            "ai_nodes": len(self.engine.brain.nodes),
            "plugins": len(self.engine.plugins.plugins),
            "ticks": self.engine.tick_count,
        }

    def _ecs_info(self, _):
        components = {}
        for comp_type in self.engine.ecs.components:
            components[comp_type] = len(self.engine.ecs.components[comp_type])
        return {
            "entities": self.engine.ecs.count(),
            "components": components,
        }

    def _ai_nodes(self, _):
        return {
            "nodes": [
                {"name": n.name, "role": n.role}
                for n in self.engine.brain.nodes.values()
            ]
        }

    def _ai_chat(self, body):
        msg = body.get("message", "")
        response = self.engine.brain.chat(msg)
        return {"response": response}

    def _config_get(self, _):
        return {"config": self.engine.config.data}

    def _config_set(self, body):
        key = body.get("key", "")
        value = body.get("value")
        self.engine.config.set(key, value)
        self.engine.config.save("configs/config.yaml")
        return {"ok": True}

    def _files_list(self, body):
        path = body.get("path", os.path.expanduser("~"))
        try:
            entries = []
            for name in sorted(os.listdir(path)):
                full = os.path.join(path, name)
                try:
                    stat = os.stat(full)
                    entries.append({
                        "name": name,
                        "is_dir": os.path.isdir(full),
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    })
                except OSError:
                    pass
            return {"path": path, "entries": entries}
        except PermissionError:
            return {"path": path, "entries": [], "error": "Permission denied"}

    def _files_read(self, body):
        path = body.get("path", "")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(1024 * 1024)  # 1MB limit
            return {"path": path, "content": content}
        except Exception as e:
            return {"error": str(e)}

    def _files_write(self, body):
        path = body.get("path", "")
        content = body.get("content", "")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"ok": True, "path": path}
        except Exception as e:
            return {"error": str(e)}

    def _terminal_exec(self, body):
        cmd = body.get("command", "")
        cwd = body.get("cwd", os.path.expanduser("~"))
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=cwd, timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}

    def _ecs_create(self, body):
        name = body.get("name", None)
        components = body.get("components", {})
        entity = self.engine.ecs.create(name)
        for comp_type, data in components.items():
            self.engine.ecs.add(entity, comp_type, data)
        return {"entity_id": entity.id}

    def _plugins_list(self, _):
        return {
            "plugins": [
                {"name": n, "enabled": e}
                for n, e in self.engine.plugins.list_plugins()
            ]
        }

    def _asset_stats(self, _):
        if hasattr(self.engine, 'assets'):
            return self.engine.assets.get_stats()
        return {"cached_assets": 0}

    def _network_stats(self, _):
        stats = {"tcp_running": False, "udp_running": False}
        if hasattr(self.engine, 'tcp_server') and self.engine.tcp_server:
            stats["tcp_running"] = self.engine.tcp_server.running
            stats["tcp_clients"] = len(self.engine.tcp_server.connections)
        if hasattr(self.engine, 'udp_socket') and self.engine.udp_socket:
            stats["udp_running"] = self.engine.udp_socket.running
            stats["udp_peers"] = len(self.engine.udp_socket.peers)
        return stats


class ChampComHTTPHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the ChampCom web interface."""

    api = None  # Set by the server

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            status, data = self.api.handle("GET", path)
            self._json_response(status, data)
        elif path == "/" or path == "/index.html":
            self._serve_dashboard()
        elif path.startswith("/static/"):
            self._serve_static(path[8:])
        else:
            self._json_response(404, {"error": "Not found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_len > 0:
            raw = self.rfile.read(content_len)
            body = json.loads(raw.decode("utf-8"))

        parsed = urllib.parse.urlparse(self.path)
        status, data = self.api.handle("POST", parsed.path, body)
        self._json_response(status, data)

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _serve_dashboard(self):
        """Serve the web-based ChampCom dashboard."""
        html = _get_dashboard_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_static(self, path):
        full_path = os.path.join("assets", path)
        if os.path.exists(full_path):
            mime, _ = mimetypes.guess_type(full_path)
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.end_headers()
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._json_response(404, {"error": "File not found"})

    def log_message(self, format, *args):
        pass  # Suppress default logging


class WebServer:
    """Runs the HTTP server in a background thread."""

    def __init__(self, engine, host="127.0.0.1", port=8470):
        self.engine = engine
        self.host = host
        self.port = port
        self.server = None

    def start(self):
        api = ChampComAPI(self.engine)
        ChampComHTTPHandler.api = api

        self.server = http.server.HTTPServer(
            (self.host, self.port), ChampComHTTPHandler
        )
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        print(f"  [WEB] HTTP server on http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()


def _get_dashboard_html():
    """Full web dashboard - accessible from any browser."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChampCom Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e0e0e0; }
  .header { background: #161b22; padding: 15px 25px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #30363d; }
  .header h1 { font-size: 20px; color: #58a6ff; }
  .header .status { color: #3fb950; font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; padding: 20px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }
  .card h2 { font-size: 14px; color: #8b949e; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
  .stat { font-size: 32px; font-weight: bold; color: #58a6ff; }
  .stat-label { font-size: 12px; color: #8b949e; margin-top: 4px; }
  .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; }
  .chat-box { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; height: 200px; overflow-y: auto; padding: 10px; margin-bottom: 10px; font-size: 13px; }
  .chat-input { display: flex; gap: 8px; }
  .chat-input input { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 13px; }
  .chat-input button { background: #238636; color: white; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; }
  .chat-input button:hover { background: #2ea043; }
  .msg-user { color: #58a6ff; }
  .msg-ai { color: #3fb950; }
  .terminal { background: #010409; border: 1px solid #30363d; border-radius: 6px; padding: 10px; font-family: 'Consolas', monospace; font-size: 12px; height: 200px; overflow-y: auto; margin-bottom: 8px; }
  .node-badge { display: inline-block; background: #238636; padding: 3px 10px; border-radius: 12px; font-size: 11px; margin: 2px; }
</style>
</head>
<body>
<div class="header">
  <h1>ChampCom Dashboard</h1>
  <div class="status" id="status">Connecting...</div>
</div>
<div class="grid">
  <div class="card">
    <h2>System Status</h2>
    <div class="stat" id="uptime">0s</div>
    <div class="stat-label">Uptime</div>
    <div class="stat-row"><span>ECS Entities</span><span id="entities">0</span></div>
    <div class="stat-row"><span>AI Nodes</span><span id="ai_nodes">0</span></div>
    <div class="stat-row"><span>Plugins</span><span id="plugins">0</span></div>
    <div class="stat-row"><span>Engine Ticks</span><span id="ticks">0</span></div>
  </div>
  <div class="card">
    <h2>AI Chat</h2>
    <div class="chat-box" id="chatbox"></div>
    <div class="chat-input">
      <input id="chatinput" placeholder="Talk to ChampCom AI..." onkeydown="if(event.key==='Enter')sendChat()">
      <button onclick="sendChat()">Send</button>
    </div>
  </div>
  <div class="card">
    <h2>Terminal</h2>
    <div class="terminal" id="termout">$ </div>
    <div class="chat-input">
      <input id="terminput" placeholder="Enter command..." onkeydown="if(event.key==='Enter')runCmd()">
      <button onclick="runCmd()">Run</button>
    </div>
  </div>
  <div class="card">
    <h2>AI Nodes</h2>
    <div id="nodelist"></div>
  </div>
</div>
<script>
  async function api(method, path, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(path, opts);
    return r.json();
  }

  async function refresh() {
    try {
      const s = await api('GET', '/api/status');
      document.getElementById('status').textContent = '● Online';
      document.getElementById('status').style.color = '#3fb950';
      const mins = Math.floor(s.uptime / 60);
      const secs = Math.floor(s.uptime % 60);
      document.getElementById('uptime').textContent = mins > 0 ? mins+'m '+secs+'s' : secs+'s';
      document.getElementById('entities').textContent = s.ecs_entities;
      document.getElementById('ai_nodes').textContent = s.ai_nodes;
      document.getElementById('plugins').textContent = s.plugins;
      document.getElementById('ticks').textContent = s.ticks.toLocaleString();

      const nodes = await api('GET', '/api/ai/nodes');
      document.getElementById('nodelist').innerHTML = nodes.nodes.map(n =>
        `<span class="node-badge">${n.name} (${n.role})</span>`
      ).join(' ');
    } catch(e) {
      document.getElementById('status').textContent = '● Offline';
      document.getElementById('status').style.color = '#f85149';
    }
  }

  async function sendChat() {
    const input = document.getElementById('chatinput');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    const box = document.getElementById('chatbox');
    box.innerHTML += `<div class="msg-user">You: ${msg}</div>`;
    const r = await api('POST', '/api/ai/chat', { message: msg });
    box.innerHTML += `<div class="msg-ai">AI: ${r.response}</div>`;
    box.scrollTop = box.scrollHeight;
  }

  async function runCmd() {
    const input = document.getElementById('terminput');
    const cmd = input.value.trim();
    if (!cmd) return;
    input.value = '';
    const term = document.getElementById('termout');
    term.innerHTML += `<span style="color:#58a6ff">$ ${cmd}</span>\\n`;
    const r = await api('POST', '/api/terminal/exec', { command: cmd });
    if (r.stdout) term.innerHTML += r.stdout;
    if (r.stderr) term.innerHTML += `<span style="color:#f85149">${r.stderr}</span>`;
    term.innerHTML += '\\n';
    term.scrollTop = term.scrollHeight;
  }

  refresh();
  setInterval(refresh, 2000);
</script>
</body>
</html>'''
