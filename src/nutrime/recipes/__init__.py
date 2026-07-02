"""Recipe corpus — seed sources, ingest adapters, vault store.

Stage 6 step 4 (Recipe sourcing) — sub-commit 4.1 lands the foundation +
TheMealDB adapter per the entry decision in ``stage3-plan.md`` § step 4.

Layout per S9 Q9.1 markdown-as-source-of-truth:
- Vault: ``<data_dir>/corpus/recipes/<recipe_id>.md``
- Body: Cooklang per D4 Q4.2 (canonical-on-ingest for all sources).
- Frontmatter: YAML per S9 Q9.2 (23 required + 8 optional fields), split
  into common base + per-type ``recipe:`` extension block per S9 Q9.3.

PHI envelope: recipe corpus lookups carry no health PHI. This package
registers a ``recipe_search`` query type with ``PhiCategory=()`` at app
init so any accidental PHI attempt fails closed per S4-Q2 discipline.
"""
