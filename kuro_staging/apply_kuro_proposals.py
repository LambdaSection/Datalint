#!/usr/bin/env python3
"""
apply_kuro_proposals.py

Purpose
- Apply the staged A-G proposal updates from `Datalint/kuro_staging/` into the
  master `kuro-rules` repository.
- Keep the operation conservative and traceable.
- Verify the copied audit script before installation.
- Update documentation and active rule text so the canonical Copilot path is
  explained consistently.
- Avoid destructive edits unless they are explicitly safe.

What this script does
1. Verifies the staging files exist.
2. Validates the staged `audit-rules.py` syntax.
3. Backs up every target file into a timestamped folder.
4. Copies staged files into `kuro-rules`:
   - `audit-rules.py`
   - `.github/workflows/rules-audit.yml`
5. Adds a local audit hook to `.pre-commit-config.yaml` if missing.
6. Updates `README.md`:
   - fixes the Windows command typo
   - documents repo mode and workspace mode
   - documents `projects.txt` policy
7. Harmonizes active rule text in:
   - `AGENTS.md`
   - `AI_GUIDELINES.md`
   - `GAD.md`
   - `.cursorrules`
   - `copilot-instructions.md`
8. Runs the installed audit in:
   - repo mode
   - workspace mode
9. Writes a summary report into the backup folder.

Notes
- This script is intentionally conservative.
- It does not delete historical logs or summaries.
- It only updates active docs and policy files.
"""

from __future__ import annotations

import datetime as dt
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    staging_dir = repo_root / "kuro_staging"
    docs_dir = repo_root.parent
    kuro_dir = docs_dir / "kuro-rules"

    if not kuro_dir.exists():
        print(f"ERROR: kuro-rules directory not found: {kuro_dir}")
        return 1

    required_staged_files = {
        "audit": staging_dir / "audit-rules.py",
        "workflow": staging_dir / "rules-audit.yml",
        "precommit": staging_dir / "pre-commit-snippet.yaml",
    }

    missing = [
        str(path) for path in required_staged_files.values() if not path.exists()
    ]
    if missing:
        print("ERROR: Missing staged files:")
        for item in missing:
            print(f"- {item}")
        return 1

    try:
        py_compile.compile(str(required_staged_files["audit"]), doraise=True)
    except py_compile.PyCompileError as exc:
        print("ERROR: staged audit-rules.py is not syntactically valid")
        print(exc)
        return 1

    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = kuro_dir / "SYNC_BACKUPS" / f"{timestamp}_apply_kuro_proposals"
    backup_dir.mkdir(parents=True, exist_ok=True)

    targets_to_backup = [
        kuro_dir / "audit-rules.py",
        kuro_dir / ".pre-commit-config.yaml",
        kuro_dir / "README.md",
        kuro_dir / "AGENTS.md",
        kuro_dir / "AI_GUIDELINES.md",
        kuro_dir / "GAD.md",
        kuro_dir / ".cursorrules",
        kuro_dir / "copilot-instructions.md",
        kuro_dir / ".github" / "workflows" / "rules-audit.yml",
    ]

    for target in targets_to_backup:
        backup_path = backup_dir / target.relative_to(kuro_dir)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.copy2(target, backup_path)

    changes: list[str] = []

    # 1. Copy staged audit script
    shutil.copy2(required_staged_files["audit"], kuro_dir / "audit-rules.py")
    changes.append("Installed audit-rules.py from staging")

    # 2. Copy staged GitHub Actions workflow
    workflow_target = kuro_dir / ".github" / "workflows" / "rules-audit.yml"
    workflow_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(required_staged_files["workflow"], workflow_target)
    changes.append("Installed .github/workflows/rules-audit.yml from staging")

    # 3. Update pre-commit config
    precommit_target = kuro_dir / ".pre-commit-config.yaml"
    precommit_text = precommit_target.read_text(encoding="utf-8")
    precommit_snippet = (
        required_staged_files["precommit"].read_text(encoding="utf-8").rstrip() + "\n"
    )

    if "id: kuro-rules-audit" not in precommit_text:
        precommit_text = precommit_text.rstrip() + "\n\n" + precommit_snippet
        precommit_target.write_text(precommit_text, encoding="utf-8")
        changes.append("Added local kuro-rules audit hook to .pre-commit-config.yaml")

    # 4. Update README
    readme_target = kuro_dir / "README.md"
    readme_text = readme_target.read_text(encoding="utf-8")

    readme_text = readme_text.replace(
        "python .udit-rules.py",
        "python .\\audit-rules.py",
    )

    if "### Audit modes" not in readme_text:
        insert_block = """
### Canonical file map

The shared AI rule system uses the following canonical file map:

- `AGENTS.md` -> project root `AGENTS.md`
- `AI_GUIDELINES.md` -> project root `AI_GUIDELINES.md`
- `GAD.md` -> project root `GAD.md`
- `.cursorrules` -> project root `.cursorrules`
- `copilot-instructions.md` -> project `.github/copilot-instructions.md`

Notes:
- `copilot-instructions.md` stored in `kuro-rules` is the master source file.
- A root-level project `copilot-instructions.md` is legacy only and should not exist.
- Sync logic and audit logic must enforce this map consistently.

### Audit modes

The audit supports two execution modes:

- `--mode repo`: validates the current `kuro-rules` repository itself.
  This is the correct mode for:
  - pre-commit
  - CI
  - pull request validation

- `--mode workspace`: validates all repositories listed in `projects.txt`
  under the workspace base directory. This is the correct mode for local
  machine-wide synchronization checks.

Examples:

Linux / macOS / WSL:

```bash
python ~/Documents/kuro-rules/audit-rules.py --mode repo --scope all
python ~/Documents/kuro-rules/audit-rules.py --mode workspace --scope all
```

Windows PowerShell:

```powershell
python .\\audit-rules.py --mode repo --scope all
python .\\audit-rules.py --mode workspace --scope all
```

### projects.txt policy

`projects.txt` is the authoritative list of tracked repositories for
workspace-wide synchronization.

Rules:
- every listed project must exist
- duplicate entries are forbidden
- stale or deleted repositories must be removed promptly
- workspace-wide audit should fail if a listed repository is missing
- repo mode must not depend on external sibling repositories
""".strip()

        marker = "## Project scaffold"
        if marker in readme_text:
            readme_text = readme_text.replace(marker, insert_block + "\n\n" + marker)
            changes.append(
                "Added canonical file map, audit modes, and projects.txt policy to README.md"
            )

    readme_target.write_text(readme_text, encoding="utf-8")

    # 5. Harmonize active rule text
    replacements = {
        kuro_dir / "AGENTS.md": [
            (
                "Rules must be consistent across AGENTS.md, AI_GUIDELINES.md, .cursorrules, copilot-instructions.md, and GAD.md.",
                "Rules must be consistent across AGENTS.md, AI_GUIDELINES.md, .cursorrules, GAD.md, and the Copilot instruction source file `copilot-instructions.md`, which is synced into project targets at `.github/copilot-instructions.md`.",
            ),
            (
                'The AI rule set (`AGENTS.md`, `AI_GUIDELINES.md`, `.cursorrules`, `copilot-instructions.md`, `GAD.md`) represents the immutable "physical laws" of the repository ecosystem.',
                'The AI rule set (`AGENTS.md`, `AI_GUIDELINES.md`, `.cursorrules`, `GAD.md`, and the master `copilot-instructions.md` source synced into `.github/copilot-instructions.md`) represents the immutable "physical laws" of the repository ecosystem.',
            ),
            (
                "3. **Cross-Project Consistency**: Shared rule files MUST not drift across projects listed in `projects.txt`.",
                "3. **Cross-Project Consistency**: Shared rule files MUST not drift across projects listed in `projects.txt`. Missing repositories and duplicate entries in `projects.txt` are policy violations.",
            ),
        ],
        kuro_dir / "AI_GUIDELINES.md": [
            (
                "- copilot-instructions.md",
                "- copilot-instructions.md (master source synced into project `.github/copilot-instructions.md` targets)",
            ),
            (
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules, GAD.md, and the master copilot-instructions.md source synced into `.github/copilot-instructions.md`) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
            ),
        ],
        kuro_dir / "GAD.md": [
            (
                "- copilot-instructions.md",
                "- copilot-instructions.md (master source synced into project `.github/copilot-instructions.md` targets)",
            ),
            (
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules, GAD.md, and the master copilot-instructions.md source synced into `.github/copilot-instructions.md`) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
            ),
        ],
        kuro_dir / ".cursorrules": [
            (
                "- copilot-instructions.md",
                "- copilot-instructions.md (master source synced into project `.github/copilot-instructions.md` targets)",
            ),
            (
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules, GAD.md, and the master copilot-instructions.md source synced into `.github/copilot-instructions.md`) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
            ),
        ],
        kuro_dir / "copilot-instructions.md": [
            (
                "- copilot-instructions.md",
                "- copilot-instructions.md (master source synced into project `.github/copilot-instructions.md` targets)",
            ),
            (
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
                'The AI rule set (AGENTS.md, AI_GUIDELINES.md, .cursorrules, GAD.md, and the master copilot-instructions.md source synced into project `.github/copilot-instructions.md`) represents the immutable "Physical Laws" of the repository ecosystem. Rules are **global** and MUST NOT vary between branches.',
            ),
        ],
    }

    for path, pairs in replacements.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in pairs:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changes.append(f"Harmonized active policy text in {path.name}")

    # 6. Execute installed audit in repo mode
    repo_mode = subprocess.run(
        [
            sys.executable,
            str(kuro_dir / "audit-rules.py"),
            "--mode",
            "repo",
            "--scope",
            "all",
            "--rules-dir",
            str(kuro_dir),
            "--base-dir",
            str(docs_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(kuro_dir),
    )

    # 7. Execute installed audit in workspace mode
    workspace_mode = subprocess.run(
        [
            sys.executable,
            str(kuro_dir / "audit-rules.py"),
            "--mode",
            "workspace",
            "--scope",
            "all",
            "--rules-dir",
            str(kuro_dir),
            "--base-dir",
            str(docs_dir),
        ],
        capture_output=True,
        text=True,
        cwd=str(kuro_dir),
    )

    report_lines = [
        "# apply_kuro_proposals report",
        "",
        f"Timestamp: {timestamp}",
        f"Repository root: {repo_root}",
        f"kuro-rules: {kuro_dir}",
        f"Backup directory: {backup_dir}",
        "",
        "## Changes applied",
    ]
    for item in changes:
        report_lines.append(f"- {item}")

    report_lines.extend(
        [
            "",
            "## Repo mode audit",
            f"Return code: {repo_mode.returncode}",
            "Stdout:",
            repo_mode.stdout.strip() or "(empty)",
            "",
            "Stderr:",
            repo_mode.stderr.strip() or "(empty)",
            "",
            "## Workspace mode audit",
            f"Return code: {workspace_mode.returncode}",
            "Stdout:",
            workspace_mode.stdout.strip() or "(empty)",
            "",
            "Stderr:",
            workspace_mode.stderr.strip() or "(empty)",
            "",
        ]
    )

    report_path = backup_dir / "apply_kuro_proposals_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Backup created at: {backup_dir}")
    print(f"Report written to: {report_path}")

    if repo_mode.returncode != 0 or workspace_mode.returncode != 0:
        print("ERROR: post-apply audit failed")
        print(report_path.read_text(encoding="utf-8"))
        return 1

    print("Success: proposals applied and validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
