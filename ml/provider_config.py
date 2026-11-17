from dataclasses import dataclass


@dataclass
class ProviderSpec:
    name: str
    mode: str
    endpoint: str | None = None
    api_key_env: str | None = None
    model_name: str | None = None
    latency_target_ms: int = 1500
    supports_multilingual: bool = False
    local_only: bool = False
    fallback_priority: int = 99


PROVIDERS: dict[str, ProviderSpec] = {
    "muse_30b": ProviderSpec(
        name="muse_30b",
        mode="local",
        model_name="Muse-30B",
        latency_target_ms=1800,
        supports_multilingual=True,
        local_only=True,
        fallback_priority=1,
    ),
    "qwen": ProviderSpec(
        name="qwen",
        mode="remote",
        endpoint="https://api.qwen.example/v1/chat/completions",
        api_key_env="QWEN_API_KEY",
        model_name="qwen-max",
        latency_target_ms=1200,
        supports_multilingual=True,
        fallback_priority=2,
    ),
    "deepseek": ProviderSpec(
        name="deepseek",
        mode="remote",
        endpoint="https://api.deepseek.com/v1/chat/completions",
        api_key_env="DEEPSEEK_API_KEY",
        model_name="deepseek-chat",
        latency_target_ms=1100,
        supports_multilingual=True,
        fallback_priority=3,
    ),
    "gemini_cli": ProviderSpec(
        name="gemini_cli",
        mode="cli_fallback",
        endpoint="gemini-cli",
        api_key_env="GEMINI_API_KEY",
        model_name="gemini-2.x",
        latency_target_ms=1400,
        supports_multilingual=True,
        fallback_priority=4,
    ),
}

# Security policy layers to keep in front of provider selection
WAF_LAYER = {
    "type": "web_application_firewall",
    "recommended": ["Cloudflare WAF", "Nginx ModSecurity", "AWS WAF"],
    "purpose": "block malicious traffic, abuse, bot traffic, and request-layer threats",
}

DAM_LAYER = {
    "type": "data_access_management",
    "recommended": ["RBAC", "secret manager", "identity verification", "field-level filtering"],
    "purpose": "protect sensitive billing, account, health, and identity data from unauthorized exposure",
}

SAFE_TASKS = {
    "general_support",
    "general_wellness",
    "onboarding",
    "faq",
    "self_help",
}

SENSITIVE_TASKS = {
    "billing",
    "account_merge",
    "security_reset",
    "identity_verification",
    "health_emergency",
    "account_recovery",
}
