# AI Code-to-App Agent

This repository includes a lightweight AI-style agent that takes source code as input and outputs a starter **app** or **website** scaffold.

## What it does

- Reads source code from a file.
- Infers likely language and high-level capabilities.
- Produces a starter project directory with:
  - `README.md` plan
  - `index.html`
  - `package.json`
  - `src/generated_logic.md` containing extracted implementation notes

## Usage

```bash
python3 agent_builder.py --input /path/to/code.py --target website --out my-site
```

or

```bash
python3 agent_builder.py --input /path/to/code.py --target app --out my-app
```

## Notes

This is a practical scaffold generator you can extend with real LLM calls (OpenAI API) for deeper code translation.
