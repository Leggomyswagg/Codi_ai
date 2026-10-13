# AI Code-to-App Agent

This repository includes a lightweight AI-style agent that takes source code as input and outputs a starter **app** or **website** scaffold.

## What it does

- Reads source code from a file.
- Infers likely language and high-level capabilities.
- Produces a runnable Vite website, or a React app with a FastAPI health-check backend:
  - `README.md` plan
  - `index.html`
  - `package.json`
  - `src/generated_logic.md` containing extracted implementation notes
  - declared frontend dependencies, source entrypoint, and build scripts
  - for apps, backend requirements and a Vite development API proxy

## Usage

```bash
python3 agent_builder.py --input /path/to/code.py --target website --out my-site
```

or

```bash
python3 agent_builder.py --input /path/to/code.py --target app --out my-app
```

## Notes

The generated README contains install, run, and build instructions. Node.js 22.12+
is required. An existing non-empty output directory is rejected to protect your work.

This generator preserves the complete input as porting notes. It does not translate
source behavior or implement inferred authentication/API/storage integrations.
Real LLM-assisted translation remains future work.

Run the generator regression tests with `python3 -m unittest -v`.
