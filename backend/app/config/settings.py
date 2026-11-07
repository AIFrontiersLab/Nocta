from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_BASE_DIR = Path("/Users/aiserver/Workspace_New/VectraFutureLab")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(DEFAULT_BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    futurelab_env: str = "development"
    base_dir: Path = DEFAULT_BASE_DIR
    timezone: str = "America/Los_Angeles"
    log_level: str = "INFO"
    futurelab_enabled: bool = True

    futurelab_api_host: str = "127.0.0.1"
    futurelab_api_port: int = 8787
    futurelab_cors_origins: str = "http://127.0.0.1:3000,http://localhost:3000"

    futurelab_database_url: str = "sqlite:///data/futurelab.db"
    futurelab_output_dir: Path = Path("outputs/futurelab")

    # SharedRoute (OpenAI-compatible). Physical backends are never contacted here.
    # Routing is done by X-Route-Project + X-Route-Task headers; model is always "router".
    openai_base_url: str = "http://10.0.0.27:8088/v1"
    openai_api_key: str = "unused"
    ai_model: str = "router"
    ai_project: str = "VectraFutureLab"
    llm_temperature: float = 0.45
    llm_timeout_seconds: float = 180.0
    llm_max_retries: int = 2

    max_runtime_minutes: int = 90
    max_model_calls: int = 80
    max_tokens: int = 250_000
    max_research_queries: int = 24
    max_prototype_cost_usd: float = 0.0
    max_parallel_agents: int = 4
    prototype_threshold: float = 80
    auto_prototype: bool = False
    require_human_approval_for_build: bool = True
    # How many prototypes (and GitHub repos) to build per daily/nightly run
    daily_prototype_count: int = 2

    score_archive_below: float = 60
    score_interesting_below: float = 70
    score_watch_below: float = 80
    score_prototype_below: float = 90

    duplicate_similarity_threshold: float = 0.78
    resurrection_min_delta: float = 8

    # Domain: FutureLab invents AI + Agentic AI only
    require_ai_agentic_scope: bool = True
    default_theme: str = "Autonomous AI Agents"

    github_token: str = ""
    github_owner: str = ""
    github_owner_is_org: bool = False
    github_auto_publish: bool = False
    github_private: bool = False
    github_repo_prefix: str = ""
    tavily_api_key: str = ""
    semantic_scholar_api_key: str = ""

    hermes_enabled: bool = False
    hermes_command: str = "hermes"
    hermes_whatsapp_group: str = ""
    futurelab_send_whatsapp: bool = False

    weight_novelty: float = 0.12
    weight_problem_severity: float = 0.10
    weight_market_potential: float = 0.08
    weight_why_now: float = 0.12
    weight_technical_feasibility: float = 0.10
    weight_competitive_white_space: float = 0.08
    weight_defensibility: float = 0.07
    weight_distribution_potential: float = 0.06
    weight_revenue_potential: float = 0.07
    weight_wow_factor: float = 0.08
    weight_prototypeability: float = 0.07
    weight_signal_confidence: float = 0.05

    @field_validator("base_dir", "futurelab_output_dir", mode="before")
    @classmethod
    def _expand_path(cls, value: object) -> Path:
        return Path(str(value)).expanduser()

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.futurelab_cors_origins.split(",") if item.strip()]

    @property
    def resolved_output_dir(self) -> Path:
        path = self.futurelab_output_dir
        return path if path.is_absolute() else self.base_dir / path

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def prompts_dir(self) -> Path:
        return self.base_dir / "backend" / "app" / "prompts"

    @property
    def database_url(self) -> str:
        url = self.futurelab_database_url
        if url.startswith("sqlite:///"):
            rest = url.removeprefix("sqlite:///")
            path = Path(rest)
            if not path.is_absolute():
                path = self.base_dir / path
            return f"sqlite:///{path}"
        return url

    @property
    def database_path(self) -> Path | None:
        url = self.database_url
        if url.startswith("sqlite:///"):
            return Path(url.removeprefix("sqlite:///"))
        return None

    @property
    def score_weights(self) -> dict[str, float]:
        return {
            "novelty": self.weight_novelty,
            "problem_severity": self.weight_problem_severity,
            "market_potential": self.weight_market_potential,
            "why_now": self.weight_why_now,
            "technical_feasibility": self.weight_technical_feasibility,
            "competitive_white_space": self.weight_competitive_white_space,
            "defensibility": self.weight_defensibility,
            "distribution_potential": self.weight_distribution_potential,
            "revenue_potential": self.weight_revenue_potential,
            "wow_factor": self.weight_wow_factor,
            "prototypeability": self.weight_prototypeability,
            "signal_confidence": self.weight_signal_confidence,
        }

    @property
    def uses_shared_route(self) -> bool:
        """True when completions go through SharedRoute (model=router)."""
        return bool(self.openai_base_url) and self.ai_model == "router"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()


def ensure_directories(settings: Settings | None = None) -> None:
    s = settings or get_settings()
    for path in (s.base_dir, s.data_dir, s.resolved_output_dir, s.logs_dir, s.prompts_dir):
        path.mkdir(parents=True, exist_ok=True)
    if s.database_path:
        s.database_path.parent.mkdir(parents=True, exist_ok=True)
