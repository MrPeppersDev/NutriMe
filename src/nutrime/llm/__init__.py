"""LLM provider adapter layer (Stage 6 sub-commit 5.2).

Per [provider-abstraction.md](../../../research/00-meta/provider-abstraction.md):
the application addresses LLM *capabilities*, not providers. Provider-specific
quirks (request shapes, error semantics, retry classification) live in adapter
modules; application code goes through :class:`nutrime.llm.client.LlmClient`,
which routes a typed request to a capability-matching provider and threads
every call through the PHI envelope -> constitutional rule engine -> audit log
pipeline landed in 5.1.

MVP-host posture (A3-v2 refinement): cloud-primary — the first registered
adapter is Anthropic. Adding Gemini or a local Ollama adapter later is a new
module implementing :class:`nutrime.llm.base.LlmProvider`, not a refactor.
"""
