from __future__ import annotations

import argparse
import json
import sys

from app.config.settings import ensure_directories, get_settings
from app.database import init_db
from app.orchestration.pipeline import run_experiment
from app.services.delivery import error_result
from app.services.seed_demo import seed_demo_data
from app.utils.logging import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vectra FutureLab — Invent tomorrow while you sleep.")
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Run an experiment")
    run_parser.add_argument("--mode", default="auto", help="Experiment mode (auto, missing-primitive, ...)")
    run_parser.add_argument("--theme", default="", help="Optional theme override")
    run_parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls")
    run_parser.add_argument("--build", action="store_true", help="Approve prototype build")
    run_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable production result JSON on stdout",
    )

    sub.add_parser("seed", help="Seed labeled demo data")
    sub.add_parser("serve", help="Start API server")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()
    setup_logging(settings.log_level)
    ensure_directories(settings)
    init_db()

    if args.command == "seed":
        seed_demo_data()
        print("Demo data seeded.")
        return 0

    if args.command == "serve":
        import uvicorn

        uvicorn.run("app.api.main:create_app", factory=True, host=settings.futurelab_api_host, port=settings.futurelab_api_port)
        return 0

    if args.command == "run" or args.command is None:
        json_output = getattr(args, "json", False)
        try:
            result = run_experiment(
                mode=getattr(args, "mode", "auto") or "auto",
                theme=getattr(args, "theme", "") or "",
                dry_run=getattr(args, "dry_run", False),
                build=getattr(args, "build", False),
            )
        except Exception as exc:
            payload = error_result(str(exc))
            if json_output:
                print(json.dumps(payload))
            else:
                print(f"Run failed: {exc}", file=sys.stderr)
            return 1

        run = result.run
        production = result.to_production_dict()
        if json_output:
            print(json.dumps(production))
        else:
            print(f"Run {run.id} completed with status={run.status} winner={run.winner_id}")
        return 0 if production["status"] == "ok" else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
