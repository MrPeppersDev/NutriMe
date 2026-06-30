"""Constitutional rule layer — hardcoded rules outside any LLM.

Per [constitutional-rules.md](../../research/00-meta/constitutional-rules.md) Rule
1 + Rule 7 enforcement note: the hardest condition-gated enforcement lives in a
deterministic hardcoded rule layer outside any LLM. T4 surfaced that adversarial
constitutional robustness does not close with parameter count alone — OSS field
has not matched Anthropic Constitutional AI / OpenAI deliberative alignment on
this dimension. Pre-MVP-ship gate is L1 — an adversarial-rule load test against
the hardcoded layer.

This module is the **scaffolding**: rule protocol, fail-closed engine, the
pre-egress validation hook used at every cloud / cross-tenant / iPhone↔server
crossing per [phi-handling.md](../../research/00-meta/phi-handling.md). Concrete
rules that depend on other components (PHI category enforcement, peer-review
floor gating, consult-professional adjacency checks) register against this
engine as those components land in later Stage 6 sub-commits.

A starter :class:`PromptInjectionGuard` ships now — the scoping doc names
prompt-injection scanning as part of the pre-egress validation surface
(stage3-plan Q2 resolution). The shipped pattern list is intentionally small;
hardening against the L1 adversarial load test happens before MVP ship.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Protocol


@dataclass(frozen=True)
class EgressRequest:
    """A payload about to cross a trust boundary.

    Boundaries that fund this check are listed in phi-handling.md "Block A
    revision" — cloud LLM, cross-tenant, iPhone↔server. The query-type id
    threads back to the PHI envelope helper (next sub-commit) so envelope-aware
    rules can look up declared category limits without re-parsing the payload.
    """

    destination: str
    query_type: str
    payload: str
    phi_categories: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class RuleResult:
    allowed: bool
    rule_name: str
    reason: str = ""


class ConstitutionalRule(Protocol):
    name: str

    def evaluate(self, request: EgressRequest) -> RuleResult: ...


class PreEgressViolation(Exception):
    """Raised when any registered rule denies an egress request.

    Fail-closed per phi-handling.md "Boundary enforcement" — boundary mistakes
    shouldn't be possible by accident; the call is rejected and the caller is
    expected to fall back to local handling or surface an error to the user.
    """

    def __init__(self, result: RuleResult) -> None:
        self.result = result
        super().__init__(
            f"egress blocked by rule {result.rule_name!r}: {result.reason}"
        )


class RuleEngine:
    def __init__(self, rules: Iterable[ConstitutionalRule] | None = None) -> None:
        self._rules: list[ConstitutionalRule] = list(rules or [])

    def register(self, rule: ConstitutionalRule) -> None:
        self._rules.append(rule)

    @property
    def rules(self) -> tuple[ConstitutionalRule, ...]:
        return tuple(self._rules)

    def evaluate_pre_egress(self, request: EgressRequest) -> None:
        for rule in self._rules:
            result = rule.evaluate(request)
            if not result.allowed:
                raise PreEgressViolation(result)


# Starter pattern set per stage3-plan Q2: prompt-injection scanning is one of
# the three pre-egress validation surfaces (alongside banned content + PHI
# category limits). Not exhaustive — the L1 load-test gate will expand this.
_PROMPT_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(ignore|disregard)\s+(the\s+|all\s+|any\s+)?(previous|prior|above)"
        r"\s+instructions",
        re.I,
    ),
    re.compile(r"forget\s+(everything|all)\b.{0,30}?\b(told|instructed|trained)", re.I),
    re.compile(r"system\s*prompt\s*:\s*", re.I),
    re.compile(r"</?\s*system\s*>", re.I),
)


class PromptInjectionGuard:
    name = "prompt-injection-guard"

    def __init__(
        self, patterns: Iterable[re.Pattern[str]] = _PROMPT_INJECTION_PATTERNS
    ) -> None:
        self._patterns = tuple(patterns)

    def evaluate(self, request: EgressRequest) -> RuleResult:
        for pattern in self._patterns:
            if pattern.search(request.payload):
                return RuleResult(
                    allowed=False,
                    rule_name=self.name,
                    reason=f"payload matched injection pattern {pattern.pattern!r}",
                )
        return RuleResult(allowed=True, rule_name=self.name)


def default_rule_engine() -> RuleEngine:
    """Engine with the starter rule set wired up.

    Components that need additional rules (PHI envelope enforcement, peer-review
    floor, consult-professional adjacency) register against the engine carried
    on the :class:`nutrime.app.Application` once the engine is in their hands.
    """
    engine = RuleEngine()
    engine.register(PromptInjectionGuard())
    return engine
