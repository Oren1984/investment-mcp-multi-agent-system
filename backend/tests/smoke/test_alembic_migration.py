"""Smoke tests for Alembic migration setup."""
from __future__ import annotations

import os
import importlib

import pytest


class TestAlembicSetup:
    def test_alembic_ini_exists(self):
        assert os.path.isfile("alembic.ini"), "alembic.ini not found in backend/"

    def test_alembic_env_importable(self):
        # alembic/env.py must be importable to catch syntax errors
        # We don't run it (it connects to DB), just parse it
        import ast
        env_path = os.path.join("alembic", "env.py")
        assert os.path.isfile(env_path), "alembic/env.py not found"
        with open(env_path) as f:
            source = f.read()
        ast.parse(source)  # raises SyntaxError if file is broken

    def test_initial_migration_exists(self):
        versions_dir = os.path.join("alembic", "versions")
        files = os.listdir(versions_dir)
        migration_files = [f for f in files if f.endswith(".py") and not f.startswith("__")]
        assert len(migration_files) >= 1, "No migration files found in alembic/versions/"

    def test_initial_migration_importable(self):
        import ast
        versions_dir = os.path.join("alembic", "versions")
        for fname in os.listdir(versions_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                with open(os.path.join(versions_dir, fname)) as f:
                    source = f.read()
                ast.parse(source)

    def test_initial_migration_has_upgrade_and_downgrade(self):
        versions_dir = os.path.join("alembic", "versions")
        for fname in os.listdir(versions_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                with open(os.path.join(versions_dir, fname)) as f:
                    source = f.read()
                assert "def upgrade" in source
                assert "def downgrade" in source
