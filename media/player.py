"""
ChampCom Media Player - Audio/video playback system
"""
import os
import subprocess
import platform
import threading


class MediaPlayer:
    """Cross-platform media player using system defaults."""

    def __init__(self):
        self.current = None
        self.playing = False
        self.volume = 0.8
        self.playlist = []
        self.playlist_index = -1

    def play(self, path):
        """Play a media file using the system's default player."""
        if not os.path.exists(path):
            return False
        self.current = path
        self.playing = True
        threading.Thread(target=self._play_system, args=(path,), daemon=True).start()
        return True

    def _play_system(self, path):
        system = platform.system()
        try:
            if system == "Linux":
                subprocess.Popen(["xdg-open", path],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            elif system == "Darwin":
                subprocess.Popen(["open", path])
            elif system == "Windows":
                os.startfile(path)
        except Exception:
            pass

    def stop(self):
        self.playing = False
        self.current = None

    def add_to_playlist(self, path):
        if os.path.exists(path):
            self.playlist.append(path)

    def next_track(self):
        if not self.playlist:
            return
        self.playlist_index = (self.playlist_index + 1) % len(self.playlist)
        self.play(self.playlist[self.playlist_index])

    def prev_track(self):
        if not self.playlist:
            return
        self.playlist_index = (self.playlist_index - 1) % len(self.playlist)
        self.play(self.playlist[self.playlist_index])

    def get_supported_formats(self):
        return {
            "audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"],
            "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"],
            "image": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"],
        }
