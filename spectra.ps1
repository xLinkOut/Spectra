param(
    [Parameter(Position = 0)]
    [string]$Command,

    [int]$Port = 8080,
    [switch]$Build,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host @"
Usage:
  .\spectra.ps1 start [-Port 8080] [-Build] [-NoOpen]
  .\spectra.ps1 stop
  .\spectra.ps1 logs
  .\spectra.ps1 status

Commands:
  start   Start Spectra with Docker Compose in background and open browser
  stop    Stop Spectra containers
  logs    Follow Spectra logs
  status  Show container status
"@
}

function Test-DockerReady {
    try {
        docker info *> $null
        return $true
    } catch {
        return $false
    }
}

function Require-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "docker command not found. Install Docker Desktop first."
    }

    if (Test-DockerReady) {
        return
    }

    Write-Host "Docker daemon not running. Trying to start Docker Desktop..."

    $candidates = @(
        "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$Env:ProgramFiles(x86)\Docker\Docker\Docker Desktop.exe",
        "$Env:LocalAppData\Programs\Docker\Docker\Docker Desktop.exe"
    )

    foreach ($exe in $candidates) {
        if (Test-Path $exe) {
            Start-Process -FilePath $exe | Out-Null
            break
        }
    }

    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 1
        if (Test-DockerReady) {
            Write-Host "Docker Desktop is ready."
            return
        }
    }

    Write-Error "Docker daemon is not running. Start Docker Desktop and retry."
}

if (-not $Command) {
    Show-Usage
    exit 1
}

Set-Location -Path $PSScriptRoot

switch ($Command.ToLowerInvariant()) {
    "start" {
        Require-Docker
        $args = @("compose", "up", "-d")
        if ($Build) {
            $args += "--build"
        }
        & docker @args

        $url = "http://localhost:$Port"
        Write-Host "Spectra is starting on $url"
        if (-not $NoOpen) {
            Start-Process $url | Out-Null
            Write-Host "Browser opened."
        }
    }

    "stop" {
        Require-Docker
        docker compose down
    }

    "logs" {
        Require-Docker
        docker compose logs -f
    }

    "status" {
        Require-Docker
        docker compose ps
    }

    "help" {
        Show-Usage
    }

    default {
        Write-Error "Unknown command: $Command"
    }
}
