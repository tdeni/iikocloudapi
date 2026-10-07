"""Command line interface of the code generator.

``python -m codegen`` regenerates the package from spec/iiko-cloud-api.json. ``--fetch`` downloads the latest
specification first and prints what changed, ``--check`` exits with status 1 if the generated files are out of date.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from codegen import spec as spec_io
from codegen.build import build
from codegen.diff import summarize
from codegen.docs import render_docs
from codegen.render import render_all
from codegen.spec import ROOT, SPEC_PATH, Spec

# Directories that are entirely generated: stale files in them are removed.
GENERATED_DIRS = ("iikocloudapi/models", "iikocloudapi/resources", "docs/reference")


def generate(raw: dict) -> dict[str, str]:
    ir = build(Spec(raw))
    files = render_all(ir)
    files.update(render_docs(ir, ROOT))
    return files


def formatted(files: dict[str, str]) -> dict[str, str]:
    """Run ``ruff format`` over the generated Python files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for rel, content in files.items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        python_files = [str(tmp_path / rel) for rel in files if rel.endswith(".py")]
        subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--quiet",
                "--config",
                str(ROOT / "pyproject.toml"),
                *python_files,
            ],
            check=True,
        )
        subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--quiet",
                "--fix-only",
                "--select",
                "I,F401",
                "--config",
                str(ROOT / "pyproject.toml"),
                *python_files,
            ],
            check=False,
        )
        subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--quiet",
                "--config",
                str(ROOT / "pyproject.toml"),
                *python_files,
            ],
            check=True,
        )
        return {rel: (tmp_path / rel).read_text(encoding="utf-8") for rel in files}


def stale_files(files: dict[str, str]) -> list[Path]:
    return [
        path
        for directory in GENERATED_DIRS
        for path in (ROOT / directory).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and str(path.relative_to(ROOT)) not in files
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m codegen", description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--fetch", action="store_true", help="download the latest specification first")
    parser.add_argument("--check", action="store_true", help="only check that generated files are up to date")
    parser.add_argument("--summary", type=Path, help="write a markdown summary of specification changes here")
    args = parser.parse_args(argv)

    raw = spec_io.load()
    if args.fetch:
        new = spec_io.fetch()
        summary = summarize(Spec(raw), Spec(new))
        print(summary)
        if args.summary:
            args.summary.write_text(summary + "\n", encoding="utf-8")
        SPEC_PATH.write_text(spec_io.dump(new), encoding="utf-8")
        raw = new

    files = formatted(generate(raw))
    changed = [
        rel for rel, content in files.items() if not (ROOT / rel).exists() or (ROOT / rel).read_text("utf-8") != content
    ]
    stale = stale_files(files)

    if args.check:
        for rel in changed:
            print(f"out of date: {rel}")
        for path in stale:
            print(f"stale: {path.relative_to(ROOT)}")
        if changed or stale:
            print("Run `python -m codegen` to regenerate.")
            return 1
        print(f"{len(files)} generated files are up to date.")
        return 0

    for rel in changed:
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[rel], encoding="utf-8")
    for path in stale:
        path.unlink()
    for directory in GENERATED_DIRS:
        for cache in (ROOT / directory).rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
    print(f"{len(changed)} file(s) written, {len(stale)} removed, {len(files)} generated in total.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
