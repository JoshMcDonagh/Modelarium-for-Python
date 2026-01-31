from __future__ import annotations

import os
from importlib import resources
from pathlib import Path


def bundled_jar_path() -> Path:
    """
    Returns the path to the JAR bundled inside this Python distribution.
    """
    pkg = resources.files("modelarium") / "_jars"
    jars = [p for p in pkg.iterdir() if p.name.endswith(".jar")]
    if not jars:
        raise FileNotFoundError("No bundled Modelarium JAR found.")
    # If there is exactly one, use it. Otherwise pick lexicographically last.
    jar = sorted(jars, key=lambda p: p.name)[-1]
    return Path(jar)


def get_jar_path() -> Path:
    """
    Prefer an override env var, otherwise use bundled jar.
    """
    override = os.environ.get("MODELARIUM_JAR")
    if override:
        return Path(override).expanduser().resolve()
    return bundled_jar_path()
