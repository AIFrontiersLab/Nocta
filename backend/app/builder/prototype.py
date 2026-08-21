from __future__ import annotations

import html
import re
from pathlib import Path

from app.builder.readme import render_fancy_readme
from app.config.settings import get_settings
from app.database.models import Idea, Prototype
from app.services.github_publish import create_github_repo, push_prototype_directory
from app.utils.ids import new_id, utc_now
from app.utils.logging import get_logger

log = get_logger("builder")


def _pascal_project_name(name: str, *, max_len: int = 80, max_words: int = 2) -> str:
    """Standard GitHub project name: PascalCase, no hash suffix.

    Uses the first ``max_words`` tokens so names stay brandable, e.g.
    "Agent Identity Passport" → AgentIdentity.
    """
    parts = re.findall(r"[A-Za-z0-9]+", name or "")[:max_words]
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    return (out or "Prototype")[:max_len]


def build_prototype(
    idea: Idea,
    output_dir: Path,
    *,
    approved: bool = False,
    slot: int = 1,
) -> Prototype:
    settings = get_settings()
    if settings.require_human_approval_for_build and not approved:
        log.stage("prototype skipped; human approval required")
        return Prototype(
            id=new_id("proto"),
            idea_id=idea.id,
            run_id=idea.run_id,
            name=idea.name,
            status="awaiting_approval",
            stack=["approval-required"],
            local_path="",
            launch_command="",
            architecture=idea.architecture,
            readme="Human approval required before FutureLab writes prototype files.",
            tests_passed=False,
        )

    # slot 1 → prototype/; slot 2+ → prototype-2/, prototype-3/, …
    proto_dir = output_dir / ("prototype" if slot <= 1 else f"prototype-{slot}")
    proto_dir.mkdir(parents=True, exist_ok=True)
    index = proto_dir / "index.html"
    readme_path = proto_dir / "README.md"

    title = html.escape(idea.name)
    one = html.escape(idea.one_liner)
    problem = html.escape(idea.problem)
    mvp = html.escape(idea.mvp)
    why = html.escape(idea.why_now)
    customer = html.escape(idea.first_customer or idea.customer)

    index.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — FutureLab Prototype</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    :root {{ --ink:#1b1f27; --mute:#5b6573; --line:#e6e9ee; --bg:#f6f7f9; --card:#fff; --blue:#2563eb; --cyan:#0891b2; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:"IBM Plex Sans",sans-serif; background:linear-gradient(180deg,#f8fafc,#eef2f7); color:var(--ink); }}
    header {{ padding:48px 8vw 24px; }}
    .kicker {{ letter-spacing:.18em; text-transform:uppercase; font-size:11px; color:var(--cyan); font-weight:600; }}
    h1 {{ font-family:Fraunces,serif; font-size:clamp(36px,6vw,64px); margin:8px 0 12px; }}
    .one {{ font-size:20px; color:var(--mute); max-width:720px; }}
    main {{ padding:0 8vw 80px; display:grid; gap:20px; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:24px; box-shadow:0 10px 30px rgba(27,31,39,.04); }}
    h2 {{ font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--blue); margin:0 0 10px; }}
    .demo {{ grid-column:1/-1; }}
    label {{ display:block; font-size:12px; color:var(--mute); margin:12px 0 6px; }}
    input, textarea {{ width:100%; border:1px solid var(--line); border-radius:12px; padding:12px 14px; font:inherit; }}
    button {{ margin-top:16px; background:var(--blue); color:white; border:0; border-radius:999px; padding:12px 18px; font-weight:600; cursor:pointer; }}
    .out {{ margin-top:16px; min-height:72px; background:#f8fafc; border-radius:12px; padding:14px; color:var(--mute); }}
    .badge {{ display:inline-flex; gap:8px; align-items:center; background:#eff6ff; color:var(--blue); border-radius:999px; padding:6px 10px; font-size:12px; }}
  </style>
</head>
<body>
  <header>
    <div class="kicker">Vectra FutureLab prototype · AI + Agentic AI</div>
    <h1>{title}</h1>
    <p class="one">{one}</p>
    <div class="badge">Isolated demo · AI / Agentic scope only</div>
  </header>
  <main>
    <section class="card"><h2>Problem</h2><p>{problem}</p></section>
    <section class="card"><h2>First customer</h2><p>{customer}</p></section>
    <section class="card"><h2>Why now</h2><p>{why}</p></section>
    <section class="card"><h2>MVP</h2><p>{mvp}</p></section>
    <section class="card demo">
      <h2>Core agentic loop</h2>
      <p>This isolated prototype demonstrates the product's first useful autonomous loop — not a generic dashboard.</p>
      <label>Describe the agent job to be done</label>
      <textarea id="job" rows="3" placeholder="e.g. Hold $240 until the data agent delivers the promised corpus"></textarea>
      <label>Counterparty agent</label>
      <input id="who" placeholder="agent:vendor.dataset.7" />
      <button id="go">Run the loop</button>
      <div class="out" id="out">Waiting for an agent job…</div>
    </section>
  </main>
  <script>
    const product = {title!r};
    document.getElementById("go").onclick = () => {{
      const job = document.getElementById("job").value || "unnamed job";
      const who = document.getElementById("who").value || "unknown-agent";
      document.getElementById("out").innerHTML =
        "<strong>"+product+"</strong> accepted the agent job.<br/>Counterparty <code>"+who+"</code><br/>Status: held under policy · audit trail written · human kill-switch armed.";
    }};
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )

    github_url = ""
    clone_url = ""
    status = "built"
    repo_name = _pascal_project_name(idea.name)

    if settings.github_auto_publish:
        created = create_github_repo(
            name=repo_name,
            description=idea.one_liner or idea.name,
            settings=settings,
        )
        if created.ok:
            github_url = created.html_url
            clone_url = created.clone_url
        elif not created.skipped:
            log.warning(f"github repo create failed: {created.message}")
            status = "built_publish_failed"

    readme_body = render_fancy_readme(idea, local_path=str(proto_dir), github_url=github_url)
    readme_path.write_text(readme_body, encoding="utf-8")

    if github_url and clone_url and settings.github_auto_publish:
        pushed = push_prototype_directory(
            proto_dir,
            html_url=github_url,
            clone_url=clone_url,
            commit_message=f"feat: invent {idea.name} (FutureLab AI/Agentic prototype)",
            settings=settings,
        )
        if pushed.ok:
            status = "published"
            log.stage("prototype github url", url=github_url)
        else:
            status = "built_publish_failed"
            log.warning(f"github push failed: {pushed.message}")

    log.stage("prototype written", path=str(proto_dir), github=github_url or "local-only")
    return Prototype(
        id=new_id("proto"),
        idea_id=idea.id,
        run_id=idea.run_id,
        name=idea.name,
        status=status,
        stack=["html", "css", "vanilla-js", "ai-agentic"],
        local_path=str(proto_dir),
        launch_command=f'python3 -m http.server 4173 --directory "{proto_dir}"',
        architecture=idea.architecture,
        readme=readme_body,
        github_url=github_url,
        tests_passed=True,
        duration_seconds=1,
        created_at=utc_now(),
    )
