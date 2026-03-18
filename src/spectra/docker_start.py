"""Helper command to start Spectra via Docker and open the app in the browser."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="spectra-start",
        description="Start Spectra with Docker Compose and open the app in your browser.",
    )
    parser.add_argument("--port", type=int, default=8080, help="Local port (default: 8080)")
    parser.add_argument("--no-build", action="store_true", help="Skip image build")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    repo_root = Path.cwd()
    compose_file = repo_root / "docker-compose.yml"
    if not compose_file.exists():
        print("Error: docker-compose.yml not found. Run this command from the project root.", file=sys.stderr)
        sys.exit(1)

    try:
        _run(["docker", "info"])
    except Exception:
        print(
            "Error: Docker daemon is not running.\n"
            "Start Docker Desktop (or Docker Engine) and retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = ["docker", "compose", "up", "-d"]
    if not args.no_build:
        cmd.append("--build")

    try:
        _run(cmd)
    except subprocess.CalledProcessError as exc:
        print(f"Error: failed to start Docker Compose (exit code {exc.returncode}).", file=sys.stderr)
        sys.exit(exc.returncode)

    url = f"http://localhost:{args.port}"
    print(f"Spectra is starting on {url}")

    if not args.no_open:
        # Small delay so the browser opens after container boot starts.
        time.sleep(1)
        webbrowser.open(url)
        print("Browser opened.")


if __name__ == "__main__":
    main()
