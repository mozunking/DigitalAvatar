"""Configurable policy engine for content safety evaluation.

Supports three evaluation checkpoints:
- pre_task: evaluate user input before task execution
- post_provider_output: evaluate LLM output before returning to user
- pre_memory_write: evaluate content before confirming memory

Rules are loaded from a JSON config file (data/policy_rules.json) or fall back
to built-in defaults.  Each rule has: pattern (regex), risk_level, checkpoint,
and message.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PolicyDecision:
    decision: str  # "allow" | "block" | "warn"
    hits: list[str] = field(default_factory=list)
    risk_level: str = "low"  # "low" | "medium" | "high"
    message: str = "allowed"


@dataclass
class PolicyRule:
    id: str
    pattern: str  # regex pattern
    checkpoint: str  # "pre_task" | "post_provider_output" | "pre_memory_write" | "all"
    risk_level: str = "high"
    message: str = "Content blocked by policy"
    _compiled: re.Pattern | None = field(default=None, repr=False)

    def compile(self) -> "PolicyRule":
        try:
            self._compiled = re.compile(self.pattern, re.IGNORECASE)
        except re.error as exc:
            logger.error("Invalid regex in policy rule %s: %s — %s", self.id, self.pattern, exc)
            self._compiled = None
        return self

    def match(self, text: str) -> bool:
        if self._compiled is None:
            return False
        return bool(self._compiled.search(text))


# ---------------------------------------------------------------------------
# Built-in default rules (used when no config file exists)
# ---------------------------------------------------------------------------

BUILTIN_RULES: list[dict[str, Any]] = [
    # Pre-task: block dangerous user instructions
    {"id": "B001", "pattern": r"steal\s+password", "checkpoint": "all", "risk_level": "high", "message": "请求包含窃取凭证指令"},
    {"id": "B002", "pattern": r"drop\s+(database|table)", "checkpoint": "all", "risk_level": "high", "message": "请求包含破坏数据库指令"},
    {"id": "B003", "pattern": r"exfiltrat\w+\s+(secret|data|credential)", "checkpoint": "all", "risk_level": "high", "message": "请求包含数据外泄指令"},
    {"id": "B004", "pattern": r"(?:rm\s+-rf|del\s+/[sS])", "checkpoint": "pre_task", "risk_level": "high", "message": "请求包含危险系统命令"},
    {"id": "B005", "pattern": r"(?:sudo|admin|root)\s+password", "checkpoint": "pre_task", "risk_level": "medium", "message": "请求包含提权相关内容"},
    {"id": "B011", "pattern": r"(?:dump|export|print|show)\s+(?:all\s+)?(?:passwords?|credentials?|tokens?|secrets?)", "checkpoint": "pre_task", "risk_level": "high", "message": "请求包含批量导出敏感凭证指令"},
    # Post-output: block obvious secret leakage from LLM
    {"id": "B006", "pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "checkpoint": "post_provider_output", "risk_level": "medium", "message": "输出疑似包含电话号码"},
    {"id": "B007", "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "checkpoint": "post_provider_output", "risk_level": "low", "message": "输出疑似包含邮箱地址"},
    {"id": "B008", "pattern": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "checkpoint": "post_provider_output", "risk_level": "medium", "message": "输出疑似包含SSN"},
    {"id": "B012", "pattern": r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----", "checkpoint": "post_provider_output", "risk_level": "high", "message": "输出疑似包含私钥材料"},
    {"id": "B013", "pattern": r"\bAKIA[0-9A-Z]{16}\b", "checkpoint": "post_provider_output", "risk_level": "high", "message": "输出疑似包含云服务访问密钥"},
    {"id": "B014", "pattern": r"\bBearer\s+[A-Za-z0-9\-_=]+(?:\.[A-Za-z0-9\-_=]+){1,2}\b", "checkpoint": "post_provider_output", "risk_level": "high", "message": "输出疑似包含访问令牌"},
    # Pre-memory: block sensitive content being persisted
    {"id": "B009", "pattern": r"(?:api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*\S+", "checkpoint": "pre_memory_write", "risk_level": "high", "message": "记忆包含密钥/令牌信息"},
    {"id": "B010", "pattern": r"(?:password|passwd|pwd)\s*[:=]\s*\S+", "checkpoint": "pre_memory_write", "risk_level": "high", "message": "记忆包含密码信息"},
    {"id": "B015", "pattern": r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----", "checkpoint": "pre_memory_write", "risk_level": "high", "message": "记忆包含私钥材料"},
    {"id": "B016", "pattern": r"\bBearer\s+[A-Za-z0-9\-_=]+(?:\.[A-Za-z0-9\-_=]+){1,2}\b", "checkpoint": "pre_memory_write", "risk_level": "high", "message": "记忆包含访问令牌"},
]


class PolicyService:
    """Singleton-like service that loads rules once and evaluates content."""

    _rules: list[PolicyRule] | None = None

    @classmethod
    def _load_rules(cls) -> list[PolicyRule]:
        if cls._rules is not None:
            return cls._rules

        rules_data = cls._read_config()
        rules: list[PolicyRule] = []
        for entry in rules_data:
            rule = PolicyRule(
                id=entry.get("id", "unknown"),
                pattern=entry["pattern"],
                checkpoint=entry.get("checkpoint", "all"),
                risk_level=entry.get("risk_level", "medium"),
                message=entry.get("message", "Blocked by policy"),
            ).compile()
            rules.append(rule)

        cls._rules = rules
        logger.info("Loaded %d policy rules", len(rules))
        return rules

    @classmethod
    def reload_rules(cls) -> None:
        """Force reload rules (useful after config change)."""
        cls._rules = None
        cls._load_rules()

    @staticmethod
    def _read_config() -> list[dict[str, Any]]:
        """Read rules from data/policy_rules.json, fallback to builtins."""
        config_path = Path("data/policy_rules.json")
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    logger.info("Using policy rules from %s", config_path)
                    return data
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to read %s: %s — using built-in rules", config_path, exc)
        return BUILTIN_RULES

    @classmethod
    def evaluate(cls, text: str, checkpoint: str) -> PolicyDecision:
        """Evaluate text against all rules matching the given checkpoint.

        Returns a PolicyDecision with:
        - decision: "block" if any high-risk rule matches, "warn" if medium, "allow" otherwise
        - hits: list of rule IDs that matched
        - risk_level: highest risk level encountered
        """
        rules = cls._load_rules()
        hits: list[str] = []
        max_risk: int = 0  # 0=low, 1=medium, 2=high
        RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

        for rule in rules:
            if rule.checkpoint != "all" and rule.checkpoint != checkpoint:
                continue
            if rule.match(text):
                hits.append(f"{checkpoint}:{rule.id}")
                risk_val = RISK_ORDER.get(rule.risk_level, 0)
                if risk_val > max_risk:
                    max_risk = risk_val

        if not hits:
            return PolicyDecision(decision="allow", hits=[], risk_level="low", message="allowed")

        # Determine decision based on highest risk level
        if max_risk >= 2:  # high
            return PolicyDecision(
                decision="block",
                hits=hits,
                risk_level="high",
                message="内容触发安全策略阻断",
            )
        elif max_risk >= 1:  # medium
            return PolicyDecision(
                decision="warn",
                hits=hits,
                risk_level="medium",
                message="内容触发安全策略警告（已记录）",
            )
        else:
            return PolicyDecision(
                decision="allow",
                hits=hits,
                risk_level="low",
                message="allowed (minor policy match)",
            )
