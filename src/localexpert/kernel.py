"""Run Python in a live IPython kernel and record every cell to a notebook.

This is the transparency layer: the agent executes code through
:class:`KernelSession`, and each execution is appended to an ``nbformat``
notebook so the whole analysis can be audited and re-run by a human.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import nbformat
from jupyter_client.manager import KernelManager
from nbformat.v4 import new_code_cell, new_notebook, new_output


@dataclass
class ExecResult:
    """Outcome of one code execution."""

    stdout: str = ""
    result: str = ""  # text/plain of the last expression, if any
    error: str = ""  # traceback text if the cell raised
    display_count: int = 0  # e.g. figures/rich outputs produced

    @property
    def ok(self) -> bool:
        return not self.error

    def as_model_text(self, max_chars: int = 4000) -> str:
        """Compact text summary handed back to the model."""
        parts: list[str] = []
        if self.stdout.strip():
            parts.append(f"[stdout]\n{self.stdout.strip()}")
        if self.result.strip():
            parts.append(f"[result]\n{self.result.strip()}")
        if self.display_count:
            parts.append(f"[display] produced {self.display_count} rich output(s) (e.g. plots)")
        if self.error.strip():
            parts.append(f"[error]\n{self.error.strip()}")
        text = "\n\n".join(parts) if parts else "[no output]"
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"
        return text


@dataclass
class KernelSession:
    """A managed IPython kernel that also records an audit notebook."""

    _km: KernelManager | None = field(default=None, init=False)
    _kc: object | None = field(default=None, init=False)
    _nb: object | None = field(default=None, init=False)

    def start(self) -> "KernelSession":
        self._km = KernelManager()
        self._km.start_kernel()
        self._kc = self._km.client()
        self._kc.start_channels()
        self._kc.wait_for_ready(timeout=60)
        self._nb = new_notebook()
        return self

    def __enter__(self) -> "KernelSession":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.shutdown()

    def execute(self, code: str, timeout: float = 120.0) -> ExecResult:
        """Run ``code``, collect its outputs, and append a notebook cell."""
        if self._kc is None:
            raise RuntimeError("KernelSession not started")

        msg_id = self._kc.execute(code)
        res = ExecResult()
        cell_outputs: list = []

        while True:
            try:
                msg = self._kc.get_iopub_msg(timeout=timeout)
            except Exception:
                res.error = res.error or f"Execution timed out after {timeout}s"
                cell_outputs.append(
                    new_output("stream", name="stderr", text=res.error)
                )
                break

            if msg["parent_header"].get("msg_id") != msg_id:
                continue

            mtype = msg["msg_type"]
            content = msg["content"]

            if mtype == "stream":
                res.stdout += content.get("text", "")
                cell_outputs.append(
                    new_output("stream", name=content.get("name", "stdout"),
                               text=content.get("text", ""))
                )
            elif mtype == "execute_result":
                data = content.get("data", {})
                res.result += data.get("text/plain", "")
                cell_outputs.append(
                    new_output("execute_result", data=data,
                               metadata=content.get("metadata", {}),
                               execution_count=content.get("execution_count"))
                )
            elif mtype == "display_data":
                res.display_count += 1
                cell_outputs.append(
                    new_output("display_data", data=content.get("data", {}),
                               metadata=content.get("metadata", {}))
                )
            elif mtype == "error":
                res.error = "\n".join(content.get("traceback", []))
                cell_outputs.append(
                    new_output("error", ename=content.get("ename", ""),
                               evalue=content.get("evalue", ""),
                               traceback=content.get("traceback", []))
                )
            elif mtype == "status" and content.get("execution_state") == "idle":
                break

        cell = new_code_cell(source=code)
        cell.outputs = cell_outputs
        self._nb.cells.append(cell)
        return res

    def save(self, path: str | Path) -> Path:
        """Write the recorded notebook to ``path``."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(self._nb, str(path))
        return path

    def shutdown(self) -> None:
        if self._kc is not None:
            self._kc.stop_channels()
            self._kc = None
        if self._km is not None:
            self._km.shutdown_kernel(now=True)
            self._km = None
