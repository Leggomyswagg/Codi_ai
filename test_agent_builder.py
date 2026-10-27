import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agent_builder import detect_language, plan_project, write_starter


class GeneratorTests(unittest.TestCase):
    def test_cli_generates_and_reports_its_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.py"
            source.write_text("print('hello')")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("agent_builder.py")),
                 "--input", str(source), "--out", str(Path(directory) / "out")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Generated website scaffold", result.stdout)

    def test_language_uses_source_extension_and_javascript_imports(self):
        self.assertEqual(detect_language("import React from 'react';"), "javascript")
        self.assertEqual(detect_language("const value = 1;", ".ts"), "typescript")
        self.assertEqual(detect_language("def login():\n    pass"), "python")

    def test_website_is_runnable_and_preserves_complete_unicode_source(self):
        source = "# café\n" + "x" * 5000
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            write_starter(output, plan_project(source, "website"), source)
            package = json.loads((output / "package.json").read_text())
            self.assertIn("vite", package["devDependencies"])
            self.assertEqual(package["scripts"]["build"], "vite build")
            self.assertIn(source, (output / "src/generated_logic.md").read_text())
            self.assertIn("src/main.js", (output / "index.html").read_text())

    def test_app_has_react_backend_and_development_proxy(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "app"
            write_starter(output, plan_project("def api(): pass", "app"), "source")
            package = json.loads((output / "package.json").read_text())
            self.assertIn("react-dom", package["dependencies"])
            self.assertIn("/api/health", (output / "backend/main.py").read_text())
            self.assertIn("8000", (output / "vite.config.js").read_text())

    def test_existing_work_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            existing = output / "index.html"
            existing.write_text("existing work")
            with self.assertRaisesRegex(ValueError, "must be empty"):
                write_starter(output, plan_project("", "website"), "")
            self.assertEqual(existing.read_text(), "existing work")


if __name__ == "__main__":
    unittest.main()
