"""Meal-plan generation (Stage 6 sub-commit 5.4) — where the tracks meet.

The planner is Track M mechanics consuming Track G's abstracted constraints
through the 5.3 seam: recipe search generates the candidate pool (the LLM
only selects from the licensed corpus, it never free-generates recipes), the
5.2 LlmClient carries each audited crossing, and the resulting plan persists
as markdown in the corpus vault per the S9 source-of-truth pattern
(``<data_dir>/corpus/plans/``; substrate denormalization deferred as usual).

A plan is *X meals across Y days*, and each meal is its own workload: its own
candidate generation, its own crossing, its own audit row, its own failure
domain. One slot failing leaves that slot unfilled rather than losing the run.
"""
