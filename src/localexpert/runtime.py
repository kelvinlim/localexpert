"""Ollama chat runtime with a tool-calling loop.

Thin wrapper over the ``ollama`` Python client. It runs a chat conversation,
dispatches ``run_python`` tool calls to the kernel, feeds results back to the
model, and loops until the model returns a final text answer (or a guard limit
is hit).
"""

from __future__ import annotations

import os
import platform
from collections.abc import Callable
from dataclasses import dataclass, field

import ollama

from .tools import RUN_PYTHON_TOOL

# Same weights, two builds. MLX is Apple's framework (needs Metal + Apple
# Silicon); it runs cleaner/faster here but cannot load on any non-Apple host.
# The GGUF build is the portable fallback (Linux, Windows x86, Intel Macs).
APPLE_SILICON_MODEL = "qwen3.5:9b-mlx"
PORTABLE_MODEL = "qwen3.5:9b"


def is_apple_silicon() -> bool:
    """True on an arm64 macOS host (M-series), where MLX models can run."""
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def default_model() -> str:
    """Pick the model: explicit env override wins, else platform-appropriate build."""
    override = os.environ.get("LOCALEXPERT_MODEL")
    if override:
        return override
    return APPLE_SILICON_MODEL if is_apple_silicon() else PORTABLE_MODEL


DEFAULT_MODEL = default_model()
DEFAULT_HOST = os.environ.get("LOCALEXPERT_OLLAMA_HOST")  # None -> ollama default


def _installed_models(client: ollama.Client) -> set[str]:
    """Names of models currently pulled in Ollama (empty set if unreachable)."""
    try:
        resp = client.list()
    except Exception:
        return set()
    models = getattr(resp, "models", None) or resp.get("models", [])
    names: set[str] = set()
    for m in models:
        name = getattr(m, "model", None) or (m.get("model") if isinstance(m, dict) else None)
        if name:
            names.add(name)
    return names
# Needs a tool-calling model. Auto-selected above: qwen3.5:9b-mlx on Apple
# Silicon, qwen3.5:9b (GGUF) elsewhere. Both fit 16 GB. Override with
# LOCALEXPERT_MODEL (e.g. qwen3.6:27b for more headroom on 32 GB).


@dataclass
class RunResult:
    """Result of a completed agent run."""

    final_text: str
    messages: list[dict]
    tool_calls: int
    stopped_on_limit: bool


@dataclass
class OllamaRuntime:
    """Drives an Ollama model through a tool-calling loop."""

    model: str = DEFAULT_MODEL
    host: str | None = DEFAULT_HOST
    max_iterations: int = 20
    # Low temperature: this is a deterministic code-writing agent, not creative
    # generation. High temperature makes smaller models emit malformed Python.
    temperature: float = 0.2
    _client: ollama.Client = field(init=False)

    def __post_init__(self) -> None:
        self._client = ollama.Client(host=self.host) if self.host else ollama.Client()
        self._maybe_fall_back_to_gguf()

    def _maybe_fall_back_to_gguf(self) -> None:
        """If the Apple-Silicon MLX model was picked but isn't pulled, use GGUF.

        The MLX and GGUF builds are separate Ollama tags, so a user who only
        pulled the portable build would otherwise hit a 'model not found' error.
        """
        if self.model != APPLE_SILICON_MODEL:
            return
        installed = _installed_models(self._client)
        if not installed or self.model in installed:
            return  # present, or Ollama unreachable — let normal errors surface
        if PORTABLE_MODEL in installed:
            print(
                f"[localexpert] {self.model} not installed; "
                f"falling back to {PORTABLE_MODEL}.",
                flush=True,
            )
            self.model = PORTABLE_MODEL

    def run(
        self,
        messages: list[dict],
        tool_dispatch: dict[str, Callable[..., str]],
        on_event: Callable[[str, str], None] | None = None,
    ) -> RunResult:
        """Run the conversation until the model stops calling tools.

        ``messages`` is the seeded conversation (system + user). ``tool_dispatch``
        maps a tool name to a callable taking the tool's parsed arguments as
        kwargs and returning a text result. ``on_event(kind, text)`` receives
        progress events for logging (kinds: ``assistant``, ``tool_call``, ``tool_result``).
        """
        messages = list(messages)
        tool_calls = 0

        for _ in range(self.max_iterations):
            response = self._client.chat(
                model=self.model,
                messages=messages,
                tools=[RUN_PYTHON_TOOL],
                options={"temperature": self.temperature},
            )
            msg = response["message"]
            messages.append(msg)

            calls = msg.get("tool_calls") or []
            if not calls:
                text = msg.get("content", "") or ""
                if on_event:
                    on_event("assistant", text)
                return RunResult(text, messages, tool_calls, stopped_on_limit=False)

            for call in calls:
                tool_calls += 1
                fn = call["function"]
                name = fn["name"]
                args = fn.get("arguments", {}) or {}
                if on_event:
                    on_event("tool_call", f"{name}({_preview(args)})")

                handler = tool_dispatch.get(name)
                if handler is None:
                    result = f"[error] unknown tool: {name}"
                else:
                    try:
                        result = handler(**args)
                    except Exception as exc:  # surface to the model, don't crash
                        result = f"[error] tool {name} raised: {exc!r}"

                if on_event:
                    on_event("tool_result", result)
                messages.append({"role": "tool", "name": name, "content": result})

        return RunResult(
            "[stopped: reached max tool iterations]",
            messages,
            tool_calls,
            stopped_on_limit=True,
        )


def _preview(args: dict, limit: int = 200) -> str:
    text = ", ".join(f"{k}={v!r}" for k, v in args.items())
    return text if len(text) <= limit else text[:limit] + "..."
