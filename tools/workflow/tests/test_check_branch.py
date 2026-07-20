"""Unit tests for the Git branch policy."""

from __future__ import annotations

import unittest

from tools.workflow.check_branch import DEFAULT_PATTERN, validate_branch


class ValidateBranchTests(unittest.TestCase):
    """Verify protected, human and automation branch names."""

    patterns = [DEFAULT_PATTERN, r"^dependabot/.+$", r"^renovate/.+$"]

    def test_rejects_protected_branch(self) -> None:
        valid, _ = validate_branch("main", ["main"], self.patterns)
        self.assertFalse(valid)

    def test_accepts_feature_branch(self) -> None:
        valid, _ = validate_branch("feat/add-login", ["main"], self.patterns)
        self.assertTrue(valid)

    def test_accepts_dependabot_branch(self) -> None:
        valid, _ = validate_branch(
            "dependabot/pip/tools/workflow/pre-commit-4.7.0",
            ["main"],
            self.patterns,
        )
        self.assertTrue(valid)

    def test_rejects_uppercase_and_spaces(self) -> None:
        valid, _ = validate_branch("Feature/Add Login", ["main"], self.patterns)
        self.assertFalse(valid)

    def test_rejects_detached_head(self) -> None:
        valid, _ = validate_branch("", ["main"], self.patterns)
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
