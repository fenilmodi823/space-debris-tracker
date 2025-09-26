#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Iterable, Tuple, Optional

ROOT = Path(r"D:\VS Code\Space Debris Tracker").resolve()
BACKEND = ROOT / "backend"

def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)

def ensure_backend() -> None:
    if not BACKEND.exists() or not (BACKEND / "__init__.py").exists():
        die(f"ERROR: backend/ or backend/__init__.py not found under {ROOT}")

def collect_internal_toplevels() -> set[str]:
    names: set[str] = set()
    for p in BACKEND.iterdir():
        if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
            names.add(p.stem)
        elif p.is_dir() and (p / "__init__.py").exists():
            names.add(p.name)
    return names

def parse_import_aliases(import_text: str) -> list[Tuple[str, Optional[str]]]:
    node = ast.parse("import " + import_text).body[0]
    assert isinstance(node, ast.Import)
    return [(n.name, n.asname) for n in node.names]

def build_backend_lines(prefix: str, aliases: Iterable[Tuple[str, Optional[str]]]) -> list[str]:
    dotted, plain = [], []
    for name, asname in aliases:
        (dotted if "." in name else plain).append((name, asname))

    lines: list[str] = []
    if plain:
        parts = []
        for name, asname in plain:
            parts.append(f"{name} as {asname}" if asname else name)
        lines.append(f"{prefix}from backend import {', '.join(parts)}")
    for name, asname in dotted:
        lines.append(f"{prefix}import backend.{name}" + (f" as {asname}" if asname else ""))
    return lines

_re_import = re.compile(r"^(?P<pre>\s*)import\s+(?P<rest>[^#\r\n]+)(?P<post>\s*(?:#.*)?)$")
_re_from   = re.compile(r"^(?P<pre>\s*)from\s+(?P<mod>[^\s]+)\s+import\s+(?P<rest>[^#\r\n]+)(?P<post>\s*(?:#.*)?)$")

def rewrite_import_line(line: str, internal: set[str]) -> Optional[str]:
    m = _re_import.match(line)
    if m:
        pre, rest, post = m.group("pre"), m.group("rest").strip(), m.group("post")
        try:
            aliases = parse_import_aliases(rest)
        except Exception:
            return None
        internal_aliases, external_aliases = [], []
        for name, asname in aliases:
            base = name.split(".")[0]
            if base in internal:
                internal_aliases.append((name, asname))
            else:
                external_aliases.append((name, asname))
        if not internal_aliases:
            return None
        new_lines: list[str] = []
        if external_aliases:
            parts = []
            for name, asname in external_aliases:
                parts.append(f"{name} as {asname}" if asname else name)
            new_lines.append(f"{pre}import {', '.join(parts)}{post}")
        backend_lines = build_backend_lines(pre, internal_aliases)
        if backend_lines:
            backend_lines[0] = backend_lines[0] + post
            new_lines.extend(backend_lines)
        return "\n".join(new_lines) + ("\n" if not line.endswith("\n") else "")
    m2 = _re_from.match(line)
    if m2:
        pre, mod, rest, post = m2.group("pre"), m2.group("mod").strip(), m2.group("rest").strip(), m2.group("post")
        if mod.startswith("backend") or mod.startswith("."):
            return None
        base = mod.split(".")[0]
        if base in internal:
            return f"{pre}from backend.{mod} import {rest}{post}\n"
    return None

def rewrite_file(path: Path, internal: set[str]) -> bool:
    original = path.read_text(encoding="utf-8")
    out, changed = [], False
    for line in original.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            out.append(line)
            continue
        new_line = rewrite_import_line(line, internal)
        if new_line is None:
            out.append(line)
        else:
            out.append(new_line)
            changed = True
    if changed:
        path.write_text("".join(out), encoding="utf-8")
    return changed

SHIM_TEMPLATE = """# Ensure project root is on sys.path when running via "python backend/scripts/..."
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO = _THIS.parents[2]  # D:\\VS Code\\Space Debris Tracker
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# You can also run this script as a module from the repo root:
#   python -m backend.scripts.{NAME}

"""

def ensure_script_shim(script_path: Path) -> bool:
    txt = script_path.read_text(encoding="utf-8")
    if "Ensure project root is on sys.path" in txt:
        return False
    block = SHIM_TEMPLATE.replace("{NAME}", script_path.stem)
    script_path.write_text(block + txt, encoding="utf-8")
    return True

def ensure_minimal_init() -> bool:
    init_path = BACKEND / "__init__.py"
    minimal = (
        '# backend/__init__.py\n'
        '__all__: list[str] = []\n'
        '__version__ = "0.1.0"\n'
    )
    current = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
    if current.strip() == minimal.strip():
        return False
    init_path.write_text(minimal, encoding="utf-8")
    return True

def main() -> None:
    ensure_backend()
    internal = collect_internal_toplevels()
    changed: list[Path] = []

    if ensure_minimal_init():
        changed.append(BACKEND / "__init__.py")

    for py in BACKEND.rglob("*.py"):
        if py.name == "__init__.py":
            continue
        if rewrite_file(py, internal):
            changed.append(py)

    scripts_dir = BACKEND / "scripts"
    if scripts_dir.exists():
        for py in scripts_dir.rglob("*.py"):
            if ensure_script_shim(py):
                changed.append(py)

    if changed:
        print("Changed files:")
        for p in changed:
            print(" -", p.relative_to(ROOT))
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()

