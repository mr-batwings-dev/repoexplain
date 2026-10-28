# repoexplain

Point it at a GitHub repo and get a Markdown write-up: overview, how the code works, the data model (with Mermaid diagrams), a directory guide, how to run it, and what to read first.

One Python file, no dependencies, free to run.

## Use

```bash
python3 repoexplain.py tiangolo/full-stack-fastapi-template
```

Accepts `owner/repo`, a GitHub URL, any git URL, or a local folder. Writes `<repo>_EXPLAINED.md` and streams it to the terminal.

| Flag | What it does |
|---|---|
| `--provider ollama\|gemini` | Local Ollama (default) or Gemini's free tier |
| `--model NAME` | Defaults: `qwen3-coder:30b`, `gemini-2.5-flash` |
| `--ask "question"` | Answer one question about the repo |
| `--sections overview,how,data,dirs,start,read` | Only some sections |
| `--no-llm` | Instant static report, no model needed |
| `--budget N` | Max chars of code sent to the model |
| `-o FILE` | Output path |

## Setup

- **Ollama (offline, free):** `ollama serve`, then `ollama pull qwen3-coder:30b` (~19GB, wants ~32GB RAM). On a smaller machine use e.g. `--model qwen2.5-coder:7b --budget 40000`.
- **Gemini (free tier, bigger context):** get a key at https://aistudio.google.com/apikey and `export GEMINI_API_KEY=...`.

Large repos don't fit in a local model's context; the tool sends the README, manifests, entry points and data-model files first. Use `--provider gemini` for big repos.

## Test

```bash
python3 -m unittest test_repoexplain.py
```
