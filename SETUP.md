# Setup — chat with a local LLM in VS Code (Mac & Windows)

This gets you a **fully local** setup: you chat with an AI in VS Code and it does the
analysis in a Jupyter notebook on your machine. Nothing is sent to the cloud, so it is
safe for sensitive data. No GitHub account or paid plan is required.

You do this **once**. After that, see [TUTORIAL.md](TUTORIAL.md) for a first analysis.

---

## What you'll install

1. **Ollama** — runs the local AI model on your laptop.
2. **uv** — sets up the Python environment in one command.
3. **VS Code** + a few extensions — the editor you'll work in.

> **Hardware:** a Mac with Apple Silicon (M-series) or a Windows 11 PC, with **16 GB RAM
> or more**. The model download is ~5–9 GB.

---

## Step 1 — Install Ollama

**macOS (Apple Silicon):** download the app from <https://ollama.com/download>, open the
`.dmg`, and drag **Ollama** to Applications. Launch it once — it runs quietly in the
background.

**Windows 11:** download `OllamaSetup.exe` from <https://ollama.com/download> and run it
(no admin rights needed). It starts automatically in the background.

## Step 2 — Install uv

Open a terminal (macOS: **Terminal**; Windows: **PowerShell**) and paste **one** line:

- **macOS:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows:** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Close and reopen the terminal afterward so `uv` is on your PATH.

## Step 3 — Create your workspace

Pick or make a folder for your work, then run (same on both OSes):

```bash
uvx --from git+https://github.com/kelvinlim/localexpert localexpert init
```

This installs everything and scaffolds the folder: a starter notebook, sample data, the
VS Code settings, and the AI "skills". It also downloads the local model (`qwen3.5:9b`) —
the first download takes a while; later runs are instant and offline.

> Prefer a permanent install? `uv tool install git+https://github.com/kelvinlim/localexpert`
> then run `localexpert init` in your folder.

## Step 4 — Install VS Code and open the folder

1. Install **VS Code**: <https://code.visualstudio.com>.
2. **File → Open Folder…** and pick the folder from Step 3.
3. When VS Code offers to **install recommended extensions**, click **Install** (this adds
   Python, Jupyter, Copilot Chat, and the Ollama connector).

## Step 5 — Point VS Code at the local model

1. Open **Copilot Chat** (chat icon in the left sidebar).
2. Switch the chat mode to **Agent** (dropdown at the top of the chat box).
3. In the model dropdown, pick your local model (e.g. `qwen3.5:9b`). If it isn't listed,
   click **Manage Models → Ollama** and add it.

You're ready — open [TUTORIAL.md](TUTORIAL.md) and do your first analysis.

---

## Keep sensitive data safe (read before using real data)

- **Confirm the selected model is your local Ollama model**, not a cloud one, before you
  open any real data. The model name in the chat box should be your `qwen3.5:9b` (or
  similar), not a hosted model.
- Turn off cloud features you don't need (telemetry, cloud/completions) in VS Code settings.
- The AI is a helper, **not** an authority: it can occasionally edit the wrong cell or make
  a statistical mistake. Read each step, and redirect it when it goes off track (see the
  tutorial's "if it goes wrong" notes).

## Troubleshooting

- **No local model in the dropdown?** Make sure Ollama is running (Step 1) and the model is
  pulled: `ollama pull qwen3.5:9b`. Then reopen the model picker.
- **The model isn't offered in Agent mode?** Agent mode only shows models that support
  tool-calling. `qwen3.5:9b` does; if you swapped models, try `qwen2.5-coder`.
- **Wrong Python/kernel?** In the notebook, click **Select Kernel** (top-right) and choose
  the `.venv` for this folder.
