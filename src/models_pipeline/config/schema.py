import dataclasses

DEFAULT_LLM_MODEL = "kilo-auto/free"
DEFAULT_LLM_API_BASE_URL = "https://api.kilo.ai/api/gateway/chat/completions"
DEFAULT_LLM_TIMEOUT_SECONDS = 300
DEFAULT_LLM_MAX_RETRIES = 2
DEFAULT_LLM_MAX_OUTPUT_TOKENS = 16_384
DEFAULT_LLM_DISABLE_THINKING = True
DEFAULT_SUMMARIZE_SOURCES_WITH_LLM = False
DEFAULT_SUMMARIZER_MODEL = DEFAULT_LLM_MODEL
DEFAULT_SUMMARIZER_API_BASE_URL = DEFAULT_LLM_API_BASE_URL
DEFAULT_SUMMARIZER_TIMEOUT_SECONDS = 120
DEFAULT_SUMMARIZER_MAX_RETRIES = 2
DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS = 16_384
DEFAULT_SUMMARIZER_DISABLE_THINKING = True
DEFAULT_MAX_CHARS_PER_SOURCE = 65_536
DEFAULT_OUTPUTS = [
    "docs/models/models.catalog.copilot.md",
    "docs/models/models.catalog.opencode.md",
    "docs/models/models.lifecycle.md",
    "docs/models/models.views.md",
]


@dataclasses.dataclass(frozen=True)
class SourceItem:
    name: str
    kind: str
    value: str
    summarize: bool | None = None
    browser: dict[str, object] = dataclasses.field(default_factory=dict)
    run: dict[str, object] = dataclasses.field(default_factory=dict)
    to_toon: bool = False


@dataclasses.dataclass(frozen=True)
class LoggingConfig:
    capture_sources: bool = False
    capture_prompts: bool = False
    capture_llm_io: bool = False
    capture_outputs: bool = False


@dataclasses.dataclass(frozen=True)
class SummarizerConfig:
    enabled: bool = DEFAULT_SUMMARIZE_SOURCES_WITH_LLM
    model: str = DEFAULT_SUMMARIZER_MODEL
    api_base_url: str = DEFAULT_SUMMARIZER_API_BASE_URL
    timeout_seconds: int = DEFAULT_SUMMARIZER_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_SUMMARIZER_MAX_RETRIES
    max_output_tokens: int = DEFAULT_SUMMARIZER_MAX_OUTPUT_TOKENS
    disable_thinking: bool = DEFAULT_SUMMARIZER_DISABLE_THINKING


@dataclasses.dataclass(frozen=True)
class LLMConfig:
    model: str = DEFAULT_LLM_MODEL
    api_base_url: str = DEFAULT_LLM_API_BASE_URL
    timeout_seconds: int = DEFAULT_LLM_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_LLM_MAX_RETRIES
    max_output_tokens: int = DEFAULT_LLM_MAX_OUTPUT_TOKENS
    disable_thinking: bool = DEFAULT_LLM_DISABLE_THINKING


@dataclasses.dataclass(frozen=True)
class PipelineConfig:
    max_chars_per_source: int = DEFAULT_MAX_CHARS_PER_SOURCE
    llm: LLMConfig = dataclasses.field(default_factory=LLMConfig)
    summarizer: SummarizerConfig = dataclasses.field(default_factory=SummarizerConfig)
    logging: LoggingConfig = dataclasses.field(default_factory=LoggingConfig)
