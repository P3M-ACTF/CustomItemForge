"""Validate the current Git branch against the repository branch policy."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence


DEFAULT_PATTERN = (
    r"^(feat|fix|docs|refactor|test|chore|perf|ci|build|style|hotfix|revert)/"
    r"[a-z0-9]+(?:-[a-z0-9]+)*$"
)


def current_branch() -> str:
    """Return the checked-out branch name, or an empty string when detached."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_branch(
    branch: str,
    protected: Sequence[str],
    patterns: Sequence[str],
) -> tuple[bool, str]:
    """Validate a branch and return a boolean plus a human-readable reason."""
    if not branch:
        return False, "Git está en estado detached HEAD; crea o selecciona una rama."

    if branch in protected:
        return False, f"La rama protegida '{branch}' no admite commits directos."

    if any(re.fullmatch(pattern, branch) for pattern in patterns):
        return True, f"La rama '{branch}' cumple la política."

    return (
        False,
        f"La rama '{branch}' no coincide con ninguno de los patrones permitidos.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Valida una rama protegida y su convención de nombre."
    )
    parser.add_argument(
        "--branch",
        help="Rama que se validará. Si se omite, se obtiene desde Git.",
    )
    parser.add_argument(
        "--protected",
        action="append",
        default=[],
        help="Rama protegida. Puede repetirse.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Expresión regular admitida. Puede repetirse.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the branch policy validator."""
    args = build_parser().parse_args(argv)
    patterns = args.pattern or [DEFAULT_PATTERN]

    try:
        branch = args.branch if args.branch is not None else current_branch()
        valid, message = validate_branch(branch, args.protected, patterns)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"No se pudo consultar Git: {error}", file=sys.stderr)
        return 2
    except re.error as error:
        print(f"La expresión regular de ramas no es válida: {error}", file=sys.stderr)
        return 2

    stream = sys.stdout if valid else sys.stderr
    print(message, file=stream)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
