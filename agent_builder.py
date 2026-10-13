#!/usr/bin/env python3
"""AI App/Web Agent scaffold.

This script accepts source code and a target type (web app or website),
then produces a runnable starter project by combining lightweight analysis
with template generation.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class ProjectPlan:
    target: str
    framework: str
    language: str
    features: List[str]


def detect_language(code: str, suffix: str = "") -> str:
    by_suffix = {".py": "python", ".js": "javascript", ".jsx": "javascript",
                 ".ts": "typescript", ".tsx": "typescript"}
    if suffix.lower() in by_suffix:
        return by_suffix[suffix.lower()]
    hints = {
        "typescript": [r"\binterface\b", r":\s*string", r"\btype\b"],
        "javascript": [r"\bfunction\b", r"\bconst\b", r"=>", r"\bimport\b.*\bfrom\b.*['\"]"],
        "python": [r"\bdef\b", r"^\s*(?:from\s+[\w.]+\s+)?import\s+[\w.]+\s*$", r":\n"],
    }
    scores: Dict[str, int] = {}
    for lang, patterns in hints.items():
        scores[lang] = sum(1 for p in patterns if re.search(p, code))
    return max(scores, key=scores.get) if any(scores.values()) else "unknown"


def infer_features(code: str) -> List[str]:
    features = []
    if re.search(r"\b(auth|login|token|jwt)\b", code, re.IGNORECASE):
        features.append("authentication")
    if re.search(r"\b(sql|database|model|schema)\b", code, re.IGNORECASE):
        features.append("data storage")
    if re.search(r"\b(api|endpoint|request|fetch)\b", code, re.IGNORECASE):
        features.append("api integration")
    if not features:
        features.append("core functionality from provided code")
    return features


def plan_project(code: str, target: str, suffix: str = "") -> ProjectPlan:
    if target not in {"app", "website"}:
        raise ValueError("Target must be app or website")
    language = detect_language(code, suffix)
    framework = "vite" if target == "website" else "fastapi+react"
    return ProjectPlan(
        target=target,
        framework=framework,
        language=language,
        features=infer_features(code),
    )


def generate_readme(plan: ProjectPlan) -> str:
    feature_lines = "\n".join(f"- {f}" for f in plan.features)
    backend = """
For the app's health-check backend, in a second terminal:
```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m uvicorn backend.main:app --reload
```
The frontend proxies `/api/health` to http://127.0.0.1:8000 during development.
For production, serve the built frontend and route `/api` to the backend.
""" if plan.target == "app" else ""
    return f"""# Generated {plan.target.title()} Starter

This project was generated from source code analysis by `agent_builder.py`.

## Plan
- Target: {plan.target}
- Framework: {plan.framework}
- Detected language in input: {plan.language}

## Inferred features
{feature_lines}

## Getting started
Use Node.js 22.12+ and npm:
```sh
npm install
npm run dev
```
Open the Vite URL printed in the terminal. `npm run build` creates `dist/`;
`npm run preview` previews that build.
{backend}
## Porting the input
This is a runnable starter, not an automatic translation of the input's behavior.
The complete source is preserved in `src/generated_logic.md` for manual porting.
Inferred capabilities above are planning notes, not implemented integrations.
"""


def write_starter(output_dir: Path, plan: ProjectPlan, source_code: str) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Output directory must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "src").mkdir(exist_ok=True)

    package_json = {
        "name": "generated-web-ui",
        "private": True,
        "type": "module",
        "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
        "engines": {"node": ">=22.12.0"},
        "devDependencies": {"vite": "8.1.4"},
    }
    if plan.target == "app":
        package_json["dependencies"] = {"react": "19.2.6", "react-dom": "19.2.6"}

    (output_dir / "README.md").write_text(generate_readme(plan), encoding="utf-8")
    (output_dir / "src" / "generated_logic.md").write_text(
        "# Porting Notes\n\n" + source_code, encoding="utf-8"
    )
    (output_dir / "package.json").write_text(json.dumps(package_json, indent=2) + "\n", encoding="utf-8")
    (output_dir / "index.html").write_text(
        """<!doctype html>
<html>
  <head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Generated App</title></head>
  <body>
    <div id='app'>Your generated app scaffold is ready.</div>
    <script type='module' src='/src/main.js'></script>
  </body>
</html>
""", encoding="utf-8"
    )
    (output_dir / ".gitignore").write_text("node_modules/\ndist/\n.venv/\n__pycache__/\n.env\n", encoding="utf-8")
    if plan.target == "app":
        (output_dir / "src" / "main.js").write_text("""import React from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [status, setStatus] = React.useState('Checking backend…');
  React.useEffect(() => {
    const controller = new AbortController();
    fetch('/api/health', { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error('Unavailable'); return response.json(); })
      .then(data => setStatus(data.status === 'ok' ? 'Backend is ready.' : 'Backend is unavailable.'))
      .catch(error => { if (error.name !== 'AbortError') setStatus('Start the backend to connect.'); });
    return () => controller.abort();
  }, []);
  return React.createElement('main', null,
    React.createElement('h1', null, 'Generated app starter'),
    React.createElement('p', null, status));
}
createRoot(document.getElementById('app')).render(React.createElement(App));
""", encoding="utf-8")
        (output_dir / "vite.config.js").write_text("""import { defineConfig } from 'vite';
export default defineConfig({ server: { proxy: { '/api': 'http://127.0.0.1:8000' } } });
""", encoding="utf-8")
        (output_dir / "backend").mkdir()
        (output_dir / "backend" / "main.py").write_text("""from fastapi import FastAPI

app = FastAPI()

@app.get('/api/health')
def health():
    return {'status': 'ok'}
""", encoding="utf-8")
        (output_dir / "backend" / "requirements.txt").write_text("fastapi==0.115.12\nuvicorn==0.34.2\n", encoding="utf-8")
    else:
        (output_dir / "src" / "main.js").write_text("""const heading = document.createElement('h1');
heading.textContent = 'Generated website starter';
document.getElementById('app').replaceChildren(heading);
""", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate app/website scaffolding from source code"
    )
    parser.add_argument("--input", required=True, help="Path to source code file")
    parser.add_argument(
        "--target",
        choices=["app", "website"],
        default="website",
        help="What to generate",
    )
    parser.add_argument("--out", default="generated-project", help="Output directory")

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    try:
        source = input_path.read_text(encoding="utf-8")
        plan = plan_project(source, args.target, input_path.suffix)
        write_starter(Path(args.out), plan, source)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    print(f"Generated {args.target} scaffold at {Path(args.out).resolve()}")
    print(f"Detected language: {plan.language}")
    print(f"Features: {', '.join(plan.features)}")


if __name__ == "__main__":
    main()
