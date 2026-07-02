"""Knowledge model — per-user atoms + synthesized entries + constraint stub.

Stage 6 step 3 (initial) — Option B (lean middle) per stage3-plan.md § Stage 6:

- Land the ``atom`` + ``synthesized_entry`` tables with the 24-column shared
  base per schema.md S1 Q1.2. Skip ``molecule`` until it has consumers.
- Populate atom rows from the step-2 intake data: ``clinical_disclosure`` for
  each allergen, ``preference_statement`` for each dietary preference,
  ``screener_result`` for each administered screener batch. Provenance +
  phi_categories tagged correctly per row.
- Populate ``synthesized_entry`` rows for the ``abstracted_constraint`` stub
  keyed off user-declared inputs only (allergens → "avoids X", preferences
  → "prefers Y"). No life-stage / DRI-derived constraints in this initial
  slice — those hit external data + trigger a targeted Stage 5 refresh, and
  are deferred to step 3 expansion or step 5 entry.

The derivation pass (``derivation.sync_from_intake``) is idempotent: existing
currently-valid atoms/entries with matching payload keys are skipped on
re-run. Retraction / supersession semantics per S1 F4 are supported by the
schema but not exercised by the initial derivation.
"""
