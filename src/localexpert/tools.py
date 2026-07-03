"""The single tool the agent is given: run Python in the kernel.

Small local models handle a minimal tool surface far better than a broad one,
so the agent gets exactly one tool. Its implementation delegates to a
:class:`~localexpert.kernel.KernelSession`.
"""

from __future__ import annotations

from .kernel import KernelSession

RUN_PYTHON_TOOL = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": (
            "Execute Python code in a persistent Jupyter kernel and return its "
            "stdout, the value of the last expression, and any errors. State "
            "(variables, imports, loaded DataFrames) persists across calls. Use "
            "this to load data, compute statistics, and generate plots."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute.",
                }
            },
            "required": ["code"],
        },
    },
}


def run_python(session: KernelSession, code: str) -> str:
    """Execute ``code`` in ``session`` and return a model-facing text summary."""
    return session.execute(code).as_model_text()
