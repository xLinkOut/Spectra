from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from spectra import docker_start


def test_main_passes_port_to_docker_compose(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "docker-compose.yml").write_text("services: {}\n")

    calls: list[tuple[list[str], str | None, dict[str, str] | None]] = []

    def fake_run(
        cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> None:
        calls.append((cmd, str(cwd) if cwd else None, env))

    opened_urls: list[str] = []

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docker_start, "_run", fake_run)
    monkeypatch.setattr(docker_start.time, "sleep", lambda _: None)
    monkeypatch.setattr(docker_start.webbrowser, "open", opened_urls.append)
    monkeypatch.setattr(
        docker_start.sys,
        "argv",
        ["spectra-start", "--port", "3000"],
    )

    docker_start.main()

    assert calls[0] == (["docker", "info"], None, None)
    assert calls[1][0] == ["docker", "compose", "up", "-d", "--build"]
    assert calls[1][1] == str(tmp_path)
    assert calls[1][2] is not None
    assert calls[1][2]["SPECTRA_PORT"] == "3000"
    assert opened_urls == ["http://localhost:3000"]


def test_main_requires_compose_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docker_start.sys, "argv", ["spectra-start"])

    with pytest.raises(SystemExit) as exc:
        docker_start.main()

    assert exc.value.code == 1


def test_main_exits_with_docker_compose_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "docker-compose.yml").write_text("services: {}\n")

    def fake_run(
        cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
    ) -> None:
        if cmd[:3] == ["docker", "compose", "up"]:
            raise subprocess.CalledProcessError(returncode=7, cmd=cmd)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docker_start, "_run", fake_run)
    monkeypatch.setattr(
        docker_start.sys,
        "argv",
        ["spectra-start", "--no-open"],
    )

    with pytest.raises(SystemExit) as exc:
        docker_start.main()

    assert exc.value.code == 7
