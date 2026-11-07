from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.config.settings import Settings, get_settings
from app.utils.logging import get_logger

log = get_logger("github_publish")

GITHUB_API = "https://api.github.com"


@dataclass
class PublishResult:
    ok: bool
    html_url: str = ""
    clone_url: str = ""
    repo_full_name: str = ""
    message: str = ""
    skipped: bool = False


def _pascal_name(name: str, *, max_len: int = 80) -> str:
    """PascalCase project name (GitHub-safe). No kebab-case or hash suffixes."""
    parts = re.findall(r"[A-Za-z0-9]+", name or "")
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    return (out or "FuturelabPrototype")[:max_len]


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), check=True, capture_output=True, text=True)


def _headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Nocta",
    }


def create_github_repo(
    *,
    name: str,
    description: str,
    settings: Settings | None = None,
) -> PublishResult:
    """Create (or reuse) a GitHub repository. Does not push code."""
    s = settings or get_settings()
    if not s.github_auto_publish:
        return PublishResult(ok=False, skipped=True, message="GITHUB_AUTO_PUBLISH is false")
    if not s.github_token:
        return PublishResult(ok=False, message="GITHUB_TOKEN missing")
    owner = (s.github_owner or "").strip()
    if not owner:
        return PublishResult(ok=False, message="GITHUB_OWNER missing")

    repo_name = _pascal_name(name)
    if s.github_repo_prefix:
        prefix = _pascal_name(s.github_repo_prefix.rstrip("-._"))
        if prefix and not repo_name.lower().startswith(prefix.lower()):
            repo_name = f"{prefix}{repo_name}"[:80]

    payload = {
        "name": repo_name,
        "description": (description or "Nocta AI/Agentic prototype")[:350],
        "private": bool(s.github_private),
        "auto_init": False,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False,
    }

    try:
        with httpx.Client(timeout=30) as client:
            if s.github_owner_is_org:
                resp = client.post(
                    f"{GITHUB_API}/orgs/{owner}/repos",
                    headers=_headers(s.github_token),
                    json=payload,
                )
            else:
                resp = client.post(
                    f"{GITHUB_API}/user/repos",
                    headers=_headers(s.github_token),
                    json=payload,
                )

            if resp.status_code == 422 and "already exists" in (resp.text or "").lower():
                existing = client.get(
                    f"{GITHUB_API}/repos/{owner}/{repo_name}",
                    headers=_headers(s.github_token),
                )
                if existing.status_code >= 400:
                    return PublishResult(
                        ok=False,
                        message=f"repo exists but fetch failed: {existing.text[:200]}",
                    )
                data = existing.json()
            elif resp.status_code >= 400:
                return PublishResult(
                    ok=False,
                    message=f"create repo failed ({resp.status_code}): {resp.text[:300]}",
                )
            else:
                data = resp.json()

        html_url = data.get("html_url") or f"https://github.com/{owner}/{repo_name}"
        clone_url = data.get("clone_url") or f"https://github.com/{owner}/{repo_name}.git"
        full = data.get("full_name") or f"{owner}/{repo_name}"
        return PublishResult(
            ok=True,
            html_url=html_url,
            clone_url=clone_url,
            repo_full_name=full,
            message="repo ready",
        )
    except Exception as exc:
        return PublishResult(ok=False, message=str(exc)[:300])


def push_prototype_directory(
    proto_dir: Path,
    *,
    html_url: str,
    clone_url: str,
    commit_message: str,
    settings: Settings | None = None,
) -> PublishResult:
    """git init/add/commit/push only inside the isolated prototype directory."""
    s = settings or get_settings()
    if not s.github_token:
        return PublishResult(ok=False, message="GITHUB_TOKEN missing")
    if not proto_dir.is_dir():
        return PublishResult(ok=False, message=f"prototype path missing: {proto_dir}")

    # Derive owner/repo from clone URL for authenticated push
    # https://github.com/owner/repo.git
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", clone_url)
    if not m:
        return PublishResult(ok=False, message="could not parse clone URL")
    owner, repo = m.group(1), m.group(2)
    push_url = f"https://x-access-token:{s.github_token}@github.com/{owner}/{repo}.git"

    try:
        if not (proto_dir / ".git").exists():
            _run(["git", "init", "-b", "main"], cwd=proto_dir)
        _run(["git", "config", "user.email", "nocta@local"], cwd=proto_dir)
        _run(["git", "config", "user.name", "Nocta"], cwd=proto_dir)

        meta = {
            "html_url": html_url,
            "clone_url": clone_url,
            "repo": f"{owner}/{repo}",
            "private": bool(s.github_private),
        }
        (proto_dir / ".nocta-github.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        _run(["git", "add", "-A"], cwd=proto_dir)
        status = _run(["git", "status", "--porcelain"], cwd=proto_dir)
        if status.stdout.strip():
            _run(["git", "commit", "-m", commit_message], cwd=proto_dir)
        remotes = _run(["git", "remote"], cwd=proto_dir)
        if "origin" in remotes.stdout.split():
            _run(["git", "remote", "set-url", "origin", push_url], cwd=proto_dir)
        else:
            _run(["git", "remote", "add", "origin", push_url], cwd=proto_dir)
        _run(["git", "push", "-u", "origin", "HEAD:main"], cwd=proto_dir)
        _run(["git", "remote", "set-url", "origin", clone_url], cwd=proto_dir)

        log.stage("prototype published to github", repo=f"{owner}/{repo}")
        return PublishResult(
            ok=True,
            html_url=html_url,
            clone_url=clone_url,
            repo_full_name=f"{owner}/{repo}",
            message="published",
        )
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or exc.stdout or str(exc))[:400].replace(s.github_token, "***")
        log.warning(f"github publish git failed: {err}")
        return PublishResult(ok=False, html_url=html_url, clone_url=clone_url, message=f"git failed: {err}")
    except Exception as exc:
        log.warning(f"github publish failed: {exc}")
        return PublishResult(ok=False, html_url=html_url, clone_url=clone_url, message=str(exc)[:300])


def publish_prototype_to_github(
    proto_dir: Path,
    *,
    name: str,
    description: str,
    settings: Settings | None = None,
) -> PublishResult:
    """Create repo + push prototype directory (single entrypoint)."""
    created = create_github_repo(name=name, description=description, settings=settings)
    if not created.ok:
        return created
    return push_prototype_directory(
        proto_dir,
        html_url=created.html_url,
        clone_url=created.clone_url,
        commit_message=f"feat: invent {name} (Nocta overnight prototype)",
        settings=settings,
    )
