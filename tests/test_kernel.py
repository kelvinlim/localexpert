"""Smoke tests for the kernel execution + audit-notebook layer (no model)."""

from __future__ import annotations

import nbformat

from localexpert.kernel import KernelSession


def test_execute_captures_stdout_and_result():
    with KernelSession() as session:
        r1 = session.execute("x = 6 * 7\nprint('hello')")
        assert r1.ok
        assert "hello" in r1.stdout
        # State persists across executions.
        r2 = session.execute("x")
        assert "42" in r2.result


def test_error_is_captured_not_raised():
    with KernelSession() as session:
        r = session.execute("1 / 0")
        assert not r.ok
        assert "ZeroDivisionError" in r.error


def test_notebook_is_saved_with_cells(tmp_path):
    nb_path = tmp_path / "audit.ipynb"
    with KernelSession() as session:
        session.execute("print('recorded')")
        session.save(nb_path)
    nb = nbformat.read(str(nb_path), as_version=4)
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"
    assert any("recorded" in o.get("text", "") for o in nb.cells[0].outputs)
