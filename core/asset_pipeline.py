"""
ChampCom Asset Pipeline - Real asset loading, caching, and hot-reload
Handles images, audio, config files, shaders, and data files.
"""
import os
import hashlib
import json
import time
import threading
from pathlib import Path


class AssetHandle:
    """Reference to a loaded asset."""

    def __init__(self, path, data, asset_type, size, checksum):
        self.path = path
        self.data = data
        self.asset_type = asset_type
        self.size = size
        self.checksum = checksum
        self.load_time = time.time()
        self.last_access = time.time()
        self.ref_count = 0

    def access(self):
        self.last_access = time.time()
        self.ref_count += 1
        return self.data


class AssetPipeline:
    """
    Real asset management system with:
    - On-demand loading
    - LRU caching with memory limits
    - File watching for hot-reload
    - Async background loading
    - Format detection
    """

    TYPES = {
        # Images
        ".png": "image", ".jpg": "image", ".jpeg": "image",
        ".gif": "image", ".bmp": "image", ".webp": "image",
        # Audio
        ".mp3": "audio", ".wav": "audio", ".ogg": "audio",
        ".flac": "audio", ".m4a": "audio",
        # Video
        ".mp4": "video", ".avi": "video", ".mkv": "video",
        ".webm": "video", ".mov": "video",
        # Data
        ".json": "data", ".yaml": "data", ".yml": "data",
        ".xml": "data", ".csv": "data",
        # Shaders
        ".vert": "shader", ".frag": "shader", ".glsl": "shader",
        ".comp": "shader", ".spv": "shader_binary",
        # Text
        ".txt": "text", ".md": "text", ".py": "text",
        ".js": "text", ".html": "text", ".css": "text",
        # Binary
        ".bin": "binary", ".dat": "binary",
    }

    def __init__(self, base_dirs=None, cache_limit_mb=256):
        self.base_dirs = base_dirs or ["assets", "configs", "modules"]
        self.cache = {}  # path -> AssetHandle
        self.cache_limit = cache_limit_mb * 1024 * 1024
        self.current_cache_size = 0
        self.lock = threading.Lock()
        self.watchers = {}  # path -> mtime
        self.on_reload = []  # callbacks for hot-reload
        self._watching = False

    def load(self, path, force=False):
        """Load an asset, using cache if available."""
        path = str(Path(path).resolve())

        with self.lock:
            if not force and path in self.cache:
                handle = self.cache[path]
                # Check if file changed on disk
                if self._file_changed(path, handle):
                    pass  # Fall through to reload
                else:
                    return handle.access()

        # Load from disk
        if not os.path.exists(path):
            return None

        ext = Path(path).suffix.lower()
        asset_type = self.TYPES.get(ext, "binary")

        # Read based on type
        if asset_type in ("text", "data", "shader"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                data = f.read()
            if asset_type == "data" and ext == ".json":
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass
        else:
            with open(path, "rb") as f:
                data = f.read()

        size = os.path.getsize(path)
        checksum = hashlib.md5(
            data.encode("utf-8") if isinstance(data, str) else data
        ).hexdigest()

        handle = AssetHandle(path, data, asset_type, size, checksum)

        with self.lock:
            self._evict_if_needed(size)
            self.cache[path] = handle
            self.current_cache_size += size
            self.watchers[path] = os.path.getmtime(path)

        return handle.access()

    def load_async(self, path, callback):
        """Load an asset in background, call callback(data) when done."""
        def _worker():
            data = self.load(path)
            callback(data)
        threading.Thread(target=_worker, daemon=True).start()

    def preload(self, directory, extensions=None):
        """Preload all assets from a directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            for f in files:
                ext = Path(f).suffix.lower()
                if extensions and ext not in extensions:
                    continue
                if ext in self.TYPES:
                    full = os.path.join(root, f)
                    self.load(full)
                    count += 1
        return count

    def unload(self, path):
        """Remove an asset from cache."""
        path = str(Path(path).resolve())
        with self.lock:
            if path in self.cache:
                self.current_cache_size -= self.cache[path].size
                del self.cache[path]
                self.watchers.pop(path, None)

    def clear_cache(self):
        with self.lock:
            self.cache.clear()
            self.current_cache_size = 0
            self.watchers.clear()

    def start_watching(self, interval=1.0):
        """Start watching loaded files for changes (hot-reload)."""
        if self._watching:
            return
        self._watching = True
        threading.Thread(target=self._watch_loop, args=(interval,),
                         daemon=True).start()

    def stop_watching(self):
        self._watching = False

    def on_asset_reload(self, callback):
        """Register callback for when any asset is hot-reloaded."""
        self.on_reload.append(callback)

    def _watch_loop(self, interval):
        while self._watching:
            changed = []
            with self.lock:
                for path, old_mtime in list(self.watchers.items()):
                    try:
                        new_mtime = os.path.getmtime(path)
                        if new_mtime != old_mtime:
                            changed.append(path)
                    except OSError:
                        pass

            for path in changed:
                self.load(path, force=True)
                for cb in self.on_reload:
                    try:
                        cb(path)
                    except Exception:
                        pass

            time.sleep(interval)

    def _file_changed(self, path, handle):
        try:
            mtime = os.path.getmtime(path)
            return mtime != self.watchers.get(path, 0)
        except OSError:
            return False

    def _evict_if_needed(self, needed_bytes):
        """LRU eviction when cache is full."""
        while (self.current_cache_size + needed_bytes > self.cache_limit
               and self.cache):
            # Find least recently accessed
            oldest_path = min(self.cache, key=lambda p: self.cache[p].last_access)
            self.current_cache_size -= self.cache[oldest_path].size
            del self.cache[oldest_path]
            self.watchers.pop(oldest_path, None)

    def get_stats(self):
        return {
            "cached_assets": len(self.cache),
            "cache_size_mb": round(self.current_cache_size / (1024 * 1024), 2),
            "cache_limit_mb": round(self.cache_limit / (1024 * 1024), 2),
            "watched_files": len(self.watchers),
        }
