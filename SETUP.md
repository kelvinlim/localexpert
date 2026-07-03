# Setup — chat with a local LLM in VS Code (Mac & Windows)

This gets you a **fully local** setup: you chat with an AI in VS Code and it does the
analysis in a Jupyter notebook on your machine. The model runs on your laptop, so your
data stays local. **No paid Copilot plan is required** — but you do need a free GitHub
sign-in, because VS Code's model picker requires being signed in (even for local models).

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

## Step 4 — Install VS Code and its extensions

1. Install **VS Code**: <https://code.visualstudio.com>.
2. **File → Open Folder…** and pick the folder from Step 3.
3. Install the extensions. VS Code *sometimes* shows an "install recommended extensions"
   banner — if it does, click **Install**. **If no banner appears** (common), install them
   yourself: open the **Extensions** panel (square icon in the left bar, or
   `Cmd/Ctrl+Shift+X`) and search for and install:
   - **GitHub Copilot Chat** (`GitHub.copilot-chat`) — the chat interface. **Required.**
   - **Python** (`ms-python.python`) and **Jupyter** (`ms-toolsai.jupyter`) — for notebooks.

   > Tip: you can also open the Command Palette (`Cmd/Ctrl+Shift+P`) and run
   > **"Extensions: Show Recommended Extensions"** to see this folder's suggested list.
   >
   > *(There is also an optional "Ollama" extension, `ollama.ollama`, that auto-detects
   > local models — but it needs VS Code 1.120+ and isn't required; Step 5 works without it.)*

## Step 5 — Connect your local model to Copilot Chat

The AI chat lives in **GitHub Copilot Chat**, and you add your local Ollama models to it:

1. Open **Copilot Chat**: press **⌃⌘I** (Mac) or **Ctrl+Alt+I** (Windows), or click the
   **chat icon in the top title bar** (the speech-bubble near the search box). It opens as a
   panel on the **right** — it is *not* in the left sidebar. Sign in to GitHub if prompted
   (free — no paid plan).
2. Click the **model dropdown** at the top of the chat box, then **Manage Models**
   (the gear / "Manage Language Models").
3. Click **Add Models**, then pick **Ollama** from the provider list. It may be labelled
   **"Ollama (Deprecated)"** — that's fine, it still works and loads your local models. VS Code
   reads your running Ollama server; select **`qwen3.5:9b`** and add it. If it's hidden in the
   picker afterward, click the **eye / Unhide** icon next to it.
   - *Non-deprecated alternative:* **Install Model Providers → Ollama** (installs the official
     `ollama.ollama` extension) — only on VS Code **1.120+**. Not required.
   - **Shortcut:** instead of steps 2–3, run **`ollama launch vscode`** in a terminal — it
     configures VS Code and shows recommended models automatically.
4. Back in the chat box, set the mode to **Agent** and select **`qwen3.5:9b`** as the model.

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

- **No Copilot Chat icon in the left sidebar?** It isn't there — Copilot Chat opens on the
  **right**. Press **⌃⌘I** (Mac) / **Ctrl+Alt+I** (Windows), or click the chat/speech-bubble
  icon in the **top title bar**.
- **No "install recommended extensions" banner?** It doesn't always appear. Just install the
  extensions by name in the Extensions panel (Step 4), or run **"Extensions: Show Recommended
  Extensions"** from the Command Palette (`Cmd/Ctrl+Shift+P`).
- **Can't find an "Ollama" extension?** You don't need one. Add your models *through* GitHub
  Copilot Chat: model dropdown → **Manage Models → Add Models → Ollama** (Step 5). In the
  provider list it appears as **"Ollama (Deprecated)"** — use it anyway, it works. Or run
  `ollama launch vscode`. The separate `ollama.ollama` extension is optional and needs VS Code
  1.120+.
- **No local model in the dropdown?** Make sure Ollama is running (Step 1), the model is pulled
  (`ollama pull qwen3.5:9b`), and you're **signed in to GitHub** (the picker needs it). Then
  redo **Manage Models → Add Models → Ollama** and click **Unhide** if the model is hidden.
- **The model isn't offered in Agent mode?** Agent mode only shows models that support
  tool-calling. `qwen3.5:9b` does; if you swapped models, try `qwen2.5-coder`.
- **Wrong Python/kernel?** In the notebook, click **Select Kernel** (top-right) and choose
  the `.venv` for this folder.
