#!/usr/bin/env python3
"""AI App/Web Agent scaffold.

This script accepts source code and a target type (web app or website),
then produces a runnable starter project by combining lightweight analysis
with template generation.
"""

from __future__ import annotations

import argparse
import json
import os
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


def detect_language(code: str) -> str:
    hints = {
        "python": [r"\bdef\b", r"\bimport\b", r":\n"],
        "javascript": [r"\bfunction\b", r"\bconst\b", r"=>"],
        "typescript": [r"\binterface\b", r":\s*string", r"\btype\b"],
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


def plan_project(code: str, target: str) -> ProjectPlan:
    language = detect_language(code)
    framework = "nextjs" if target == "website" else "fastapi+react"
    return ProjectPlan(
        target=target,
        framework=framework,
        language=language,
        features=infer_features(code),
    )


def generate_readme(plan: ProjectPlan) -> str:
    feature_lines = "\n".join(f"- {f}" for f in plan.features)
    return f"""# Generated {plan.target.title()} Starter

This project was generated from source code analysis by `agent_builder.py`.

## Plan
- Target: {plan.target}
- Framework: {plan.framework}
- Detected language in input: {plan.language}

## Inferred features
{feature_lines}

## Getting started
1. Install dependencies from each package folder.
2. Run backend and frontend dev servers.
3. Replace placeholders in `/src/generated_logic.md` with real implementation details.
"""


def write_starter(output_dir: Path, plan: ProjectPlan, source_code: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "src").mkdir(exist_ok=True)

    package_json = {
        "name": "generated-web-ui",
        "private": True,
        "scripts": {"dev": "vite", "build": "vite build"},
    }

    (output_dir / "README.md").write_text(generate_readme(plan))
    (output_dir / "src" / "generated_logic.md").write_text(
        "# Porting Notes\n\n" + source_code[:4000]
    )
    (output_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    (output_dir / "index.html").write_text(
        """<!doctype html>
<html>
  <head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Generated App</title></head>
  <body>
    <div id='app'>Your generated app scaffold is ready.</div>
  </body>
</html>
"""
    )


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

    source = input_path.read_text(encoding="utf-8")
    plan = plan_project(source, args.target)
    write_starter(Path(args.out), plan, source)

    print(f"Generated {args.target} scaffold at {os.path.abspath(args.out)}")
    print(f"Detected language: {plan.language}")
    print(f"Features: {', '.join(plan.features)}")


if __name__ == "__main__":
    main()
