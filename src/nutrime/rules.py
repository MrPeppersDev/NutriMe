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
from typing import TYPE_CHECKING, Callable, Iterable, Protocol

if TYPE_CHECKING:
    from nutrime.phi import PhiEnvelopeRegistry


@dataclass(frozen=True)
class EgressRequest:
    """A payload about to cross a trust boundary.

    Boundaries that fund this check are listed in phi-handling.md "Block A
    revision" — cloud LLM, cross-tenant, iPhone↔server. The query-type id
    threads back to the PHI envelope helper (next sub-commit) so envelope-aware
    rules can look up declared category limits without re-parsing the payload.

    ``request_id`` correlates the crossing to its ``op_llm_request_log`` row +
    substrate counterparts per S8 Q8.1; callers that go on to make an LLM call
    should set it so the audit trail joins up.
    """

    destination: str
    query_type: str
    payload: str
    phi_categories: frozenset[str] = field(default_factory=frozenset)
    request_id: str | None = None


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


PreEgressObserver = Callable[[EgressRequest, "RuleResult"], None]


class RuleEngine:
    def __init__(self, rules: Iterable[ConstitutionalRule] | None = None) -> None:
        self._rules: list[ConstitutionalRule] = list(rules or [])
        self._observers: list[PreEgressObserver] = []

    def register(self, rule: ConstitutionalRule) -> None:
        self._rules.append(rule)

    def add_observer(self, observer: PreEgressObserver) -> None:
        """Observers see every pre-egress verdict — allowed and blocked.

        Wired by :func:`nutrime.audit.attach_pre_egress_audit` per issue #22.
        An observer exception propagates and therefore blocks the crossing:
        fail-closed, because an unaudited egress cannot be backfilled.
        """
        self._observers.append(observer)

    @property
    def rules(self) -> tuple[ConstitutionalRule, ...]:
        return tuple(self._rules)

    def _notify(self, request: EgressRequest, result: RuleResult) -> None:
        for observer in self._observers:
            observer(request, result)

    def evaluate_pre_egress(self, request: EgressRequest) -> None:
        for rule in self._rules:
            result = rule.evaluate(request)
            if not result.allowed:
                self._notify(request, result)
                raise PreEgressViolation(result)
        self._notify(
            request, RuleResult(allowed=True, rule_name="pre-egress")
        )


# Pattern set per stage3-plan Q2: prompt-injection scanning is one of the
# three pre-egress validation surfaces (alongside banned content + PHI
# category limits). Expanded 2026-10-04 by the L1 adversarial harness
# (tests/test_rules_adversarial.py — issue #6): obfuscation-tolerant
# separators, role-override, exfiltration-bait and tag-smuggling families
# added after the harness demonstrated bypasses of the starter set.
# \W* between tokens defeats zero-width/punctuation splitting after the
# payload is NFKC-normalized by normalize_for_scan().
_PROMPT_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(ignore|disregard|bypass|override)[\W_]*(the[\W_]*|all[\W_]*|any[\W_]*)?"
        r"(previous|prior|above|earlier|preceding|original)[\W_]*"
        r"(instruction|rule|constraint|direction|prompt|guideline)",
        re.I,
    ),
    re.compile(
        r"forget[\W_]*(everything|all)\b.{0,40}?\b(told|instructed|trained|said)",
        re.I | re.S,
    ),
    re.compile(r"system[\W_]*prompt[\W_]*[:=]", re.I),
    re.compile(r"<[\W_]*/?[\W_]*(system|assistant|instructions?)[\W_]*>", re.I),
    re.compile(r"\[[\W_]*(system|inst)[\W_]*\]", re.I),
    # Role-override family: "you are now…", "act as…", "new persona"
    re.compile(
        r"\byou[\W_]*are[\W_]*(now|no[\W_]*longer)\b.{0,60}?"
        r"\b(assistant|ai|model|rule|restriction|filter|unrestricted)",
        re.I | re.S,
    ),
    re.compile(
        r"\b(act|behave|respond)[\W_]*as[\W_]*(if[\W_]*)?(an?[\W_]*)?"
        r"(unrestricted|unfiltered|jailbroken|developer[\W_]*mode|dan\b)",
        re.I,
    ),
    # Exfiltration bait: asking the downstream model to echo hidden context
    re.compile(
        r"\b(repeat|print|reveal|output|show)\b.{0,40}?"
        r"\b(system[\W_]*prompt|hidden|initial[\W_]*instruction|above[\W_]*text|"
        r"everything[\W_]*before)",
        re.I | re.S,
    ),
    # Instruction-smuggling markers common in indirect injection via content
    re.compile(r"\bAI[\W_]*:[\W_]*(you|please|now)\b", re.I),
    re.compile(r"\bimportant[\W_]*(new|updated)[\W_]*instructions?\b", re.I),
)

_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)


def normalize_for_scan(payload: str) -> str:
    """Canonicalize before pattern matching (L1 hardening).

    NFKC folds fullwidth/stylized unicode back to ASCII ("ｉｇｎｏｒｅ" →
    "ignore"); zero-width characters are stripped so they can't split
    tokens invisibly. Patterns then tolerate visible separators via \\W*.
    """
    import unicodedata

    return unicodedata.normalize("NFKC", payload).translate(_ZERO_WIDTH)


class PromptInjectionGuard:
    name = "prompt-injection-guard"

    def __init__(
        self, patterns: Iterable[re.Pattern[str]] = _PROMPT_INJECTION_PATTERNS
    ) -> None:
        self._patterns = tuple(patterns)

    def evaluate(self, request: EgressRequest) -> RuleResult:
        normalized = normalize_for_scan(request.payload)
        # Second scan surface: everything non-alphanumeric stripped, which
        # collapses per-character splitting ("i.g.n.o.r.e …") that survives
        # token-level \W* tolerance. Patterns' [\W_]* match empty here.
        condensed = re.sub(r"[^a-z0-9]", "", normalized.lower())
        for pattern in self._patterns:
            if pattern.search(normalized) or pattern.search(condensed):
                return RuleResult(
                    allowed=False,
                    rule_name=self.name,
                    reason=f"payload matched injection pattern {pattern.pattern!r}",
                )
        return RuleResult(allowed=True, rule_name=self.name)


def default_rule_engine(
    phi_envelope_registry: PhiEnvelopeRegistry | None = None,
) -> RuleEngine:
    """Engine with the starter rule set wired up.

    Components that need additional rules (peer-review floor,
    consult-professional adjacency) register against the engine carried on the
    :class:`nutrime.app.Application` once the engine is in their hands.
    """
    from nutrime.phi import PhiEnvelopeRule, default_phi_envelope_registry

    registry = phi_envelope_registry or default_phi_envelope_registry()
    engine = RuleEngine()
    engine.register(PromptInjectionGuard())
    engine.register(PhiEnvelopeRule(registry))
    return engine
