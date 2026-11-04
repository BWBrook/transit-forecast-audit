"""Capture reproducibility metadata without reading environment variables/secrets."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    packages = {}
    for name in ("numpy", "astropy", "scipy", "pandas", "matplotlib", "transit-forecast-audit"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True)
    output = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.system(),
        "machine_architecture": platform.machine(), "packages": packages,
        "git_commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "note": "Environment observation, not a portable dependency lock. No credentials captured.",
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(path)


if __name__ == "__main__":
    main()
