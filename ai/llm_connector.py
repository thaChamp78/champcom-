"""
ChampCom LLM Connector - REAL API connections to OpenAI and Anthropic
Uses only urllib (stdlib) - no external packages needed.
"""
import json
import urllib.request
import urllib.error
import os


class LLMConnector:
    """
    Real LLM API connector. Supports:
    - Anthropic (Claude)
    - OpenAI (GPT)
    - Local echo mode (no API key needed)
    """

    def __init__(self, provider="local", api_key="", model=""):
        self.provider = provider
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
        self.model = model
        self.history = []

        # Auto-detect provider from API key
        if not provider or provider == "auto":
            if self.api_key.startswith("sk-ant-"):
                self.provider = "anthropic"
                self.model = model or "claude-sonnet-4-20250514"
            elif self.api_key.startswith("sk-"):
                self.provider = "openai"
                self.model = model or "gpt-4"
            else:
                self.provider = "local"

    def chat(self, message, system_prompt="You are ChampCom AI, a helpful assistant."):
        """Send a message and get a response."""
        self.history.append({"role": "user", "content": message})

        if self.provider == "anthropic":
            response = self._call_anthropic(message, system_prompt)
        elif self.provider == "openai":
            response = self._call_openai(message, system_prompt)
        else:
            response = self._local_response(message)

        self.history.append({"role": "assistant", "content": response})
        return response

    def _call_anthropic(self, message, system_prompt):
        """Real Anthropic API call using urllib."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": self.history[-20:],  # Last 20 messages for context
        }

        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"),
                headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.readable() else str(e)
            return f"[API Error {e.code}] {error_body}"
        except Exception as e:
            return f"[Connection Error] {e}"

    def _call_openai(self, message, system_prompt):
        """Real OpenAI API call using urllib."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.history[-20:])

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
        }

        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"),
                headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.readable() else str(e)
            return f"[API Error {e.code}] {error_body}"
        except Exception as e:
            return f"[Connection Error] {e}"

    def _local_response(self, message):
        """Offline pattern-matching response (no API needed)."""
        msg = message.lower()
        if any(w in msg for w in ["hello", "hi", "hey"]):
            return "Hello! I'm ChampCom AI. How can I help you?"
        if "help" in msg:
            return ("I can help with: file management, system info, "
                    "planning tasks, and general questions. "
                    "Set an API key in Settings to unlock full AI.")
        if "status" in msg:
            return "All ChampCom systems operational."
        if any(w in msg for w in ["time", "date"]):
            import time
            return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        return f"I understand: '{message}'. Configure an API key for full AI responses."

    def clear_history(self):
        self.history.clear()

    def get_provider_info(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "history_length": len(self.history),
        }
