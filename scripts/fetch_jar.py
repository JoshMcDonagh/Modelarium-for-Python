from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
JARS_DIR = ROOT / "modelarium" / "_jars"


def load_cfg() -> dict:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    cfg = data.get("tool", {}).get("modelarium", {})
    required = ["java_group_id", "java_artifact_id", "java_version"]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise RuntimeError(f"Missing {missing} in [tool.modelarium] in pyproject.toml")
    return cfg


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r:
        dest.write_bytes(r.read())


def main() -> int:
    cfg = load_cfg()
    group = cfg["java_group_id"]
    artifact = cfg["java_artifact_id"]
    version = cfg["java_version"]

    group_path = group.replace(".", "/")
    jar_name = f"{artifact}-{version}.jar"
    jar_url = f"https://repo1.maven.org/maven2/{group_path}/{artifact}/{version}/{jar_name}"

    JARS_DIR.mkdir(parents=True, exist_ok=True)
    jar_path = JARS_DIR / jar_name

    # Allow overriding via env var (MODELARIUM_JAR_URL) if you ever want:
    jar_url = os.environ.get("MODELARIUM_JAR_URL", jar_url)

    print(f"Fetching JAR: {jar_url}")
    download(jar_url, jar_path)
    print(f"Saved: {jar_path}")
    print(f"SHA256: {sha256(jar_path)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
