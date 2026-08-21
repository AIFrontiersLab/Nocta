from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
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

    llm_provider: str = "ollama"
    llm_base_url: str = "http://10.0.0.25:11434/v1"
    llm_temperature: float = 0.45
    llm_timeout_seconds: int = 180
    llm_max_retries: int = 2
    ollama_model: str = "qwen3.6:27b"
    llm_filter_model: str = "qwen3.6:27b"
    llm_reasoning_model: str = "qwen3.6:27b"
    llm_coding_model: str = "qwen3.6:27b"
    llm_default_model: str = "qwen3.6:27b"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    ollama_host: str = "http://10.0.0.25:11434"
    ollama_fallback_host: str = "http://localhost:11434"
    # Used for every model tier when primary Ollama is unreachable
    ollama_fallback_model: str = "qwen3.5:latest"

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
    github_private: bool = True
    github_repo_prefix: str = "futurelab"
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

    def model_for_tier(self, tier: str) -> str:
        mapping = {
            "filter": self.llm_filter_model,
            "cheap": self.llm_filter_model,
            "reasoning": self.llm_reasoning_model,
            "strong": self.llm_reasoning_model,
            "coding": self.llm_coding_model,
            "default": self.llm_default_model,
        }
        return mapping.get(tier) or self.llm_default_model or self.ollama_model


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
