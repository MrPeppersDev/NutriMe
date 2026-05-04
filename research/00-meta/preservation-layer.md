# NutriMe — Preservation Layer

> Once content has been verified + integrated into NutriMe's corpus, the system becomes its own preservation layer. If the original source later disappears (site reorg, content removal, site shutdown), NutriMe's copy is the preserved version. Source disappearance is a *content-preservation event*, not a deletion trigger.

This is a foundational principle that emerged during [architecture.md E4 dialogue](architecture.md#e4--update-cadence--corpus-refresh-design) and applies broadly across the corpus.

## The principle

NutriMe's corpus is **archival, not derivative**. The B3 cache+freshness model assumes the source IS the source-of-truth, with NutriMe as a freshness-tracking cache. This principle says: once content passes verification + integration, **NutriMe takes preservation responsibility**.

When a source removes content NutriMe already holds:

- **404 / source-removed isn't "delete locally"** — it's "the source no longer carries this; our copy is the preserved version"
- **Provenance frontmatter records the state transition** — *originally sourced from X on date Y; X removed the source on date Z; preserved here under [original license terms]*
- **Staleness indicator shifts framing** — instead of *"stale: source-of-truth disagrees,"* it becomes *"preserved: source no longer carries this content"*
- **Re-verification cannot happen** when the source is gone — content stays in corpus indefinitely, preservation context surfaced honestly per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty)

## Where this applies

This principle was surfaced during the recipe corpus discussion but applies system-wide to any content NutriMe has integrated where the source might disappear:

- **Recipes** (per [sweep #11](../11-recipe-sourcing/scope.md)) — the originating example. Sites reorg, take recipes down, or shut down; NutriMe's ingested copy survives.
- **Regulatory PDFs** (per [sweep #10 + dynamic-research-expansion](../10-clinical-condition-gating/scope.md)) — agencies pull PDFs, replace them with newer versions, retire whole guidance documents. NutriMe's copy of what was authoritative at ingestion is preserved.
- **Peer-reviewed papers** behind dead URLs — papers behind subscription paywalls, journals shut down, DOIs rot. NutriMe's extracted claims + provenance stay valid.
- **Vendor documentation** taken down — drug labels updated + old versions removed; supplement-vendor sites shut down. Old versions stay in corpus.
- **Cuisine + technique knowledge** — culinary blogs disappear; institutional academy content reorganized; cookbook author sites shut down. Ingested knowledge is preserved.
- **Educational content** — health-info sites get acquired + content scrubbed; old advice gets retired. Preserved with clear provenance about when it was current.

## License posture

**Original-source license terms still apply.** If content was Apache-2.0-or-CC-BY-licensed at ingestion, those terms are recorded in frontmatter and continue to govern our preservation regardless of the source's later actions. License grants don't disappear just because the source did.

**Two notable exceptions:**

- **ToS-revocation cases** — if a site removes content for explicit ToS reasons (creator revoking distribution rights, copyright claim, legal takedown), NutriMe should honor the revocation by removing or restricting the preserved copy. This is rare and case-by-case.
- **Privacy-driven removals** — if content is removed because it contained PII or PHI of a third party (rare for our corpus types but possible), NutriMe respects the privacy concern.

For routine source disappearance — site cleanup, site shutdown, content reorganization — the license that was granted at ingestion continues to govern our preservation.

## Bitemporal lifecycle integration

Per [A4 + B4 bitemporal lifecycle](architecture.md#a4--data-persistence--knowledge-model-storage):

- **`valid_from`** — when NutriMe ingested + verified the content
- **`valid_until`** — null while content is preserved + accessible; populated only if explicitly retracted (rare)
- **New frontmatter field — `source_removed_at`** — when the source was observed to no longer carry the content
- **New frontmatter field — `source_status`** — one of: `active` (source still carries content) / `superseded` (source replaced with newer version we've also ingested) / `removed` (source no longer carries) / `revoked` (source explicitly revoked distribution rights)

When the user views preserved content, the surface honestly notes its preservation status.

## Re-verification handling

When E4 quarterly re-verification cycles encounter content whose source has disappeared:

- **No retry / re-fetch attempts** for content marked `source_status: removed` — verification can't happen against a missing source
- **Cycle reports the preservation transition** — *"Content X was previously sourced from Y; Y no longer serves; content is now in preservation status"*
- **User-facing surfaces show the transition** — staleness-indicator framing shifts from "freshness check pending" to "preserved (source no longer carries this content)"

## Why this matters for NutriMe

Three reasons this principle is load-bearing:

1. **Recipe corpus integrity** — losing recipes that the user has cooked + liked + relied on because the source site reorganized would be a significant trust break. The corpus is the user's accumulated trusted recipe library.
2. **Audit trail integrity** — Rule 8 epistemic trail surfaces what content fed an inference. If content disappears retroactively, the trail breaks. Preservation keeps the trail intact.
3. **Publication target reproducibility** — for publication targets #4 + #5 (aggregate data publications), the underlying content that fed inferences must remain accessible to support reproducibility per [E1 dual data lineage](architecture.md#e1--data-collection-schema-for-reproducibility). Preservation makes reproducibility possible across time.

## Source

User direction (2026-05-03, Stage 3 E4 Q4.4 dialogue):
> "If we've logged recipes and the site no longer serves that recipe but it was a good one, we don't want to lose it just because it doesn't serve it anymore."

## Related

- [architecture.md E4](architecture.md#e4--update-cadence--corpus-refresh-design) — full Stage 3 resolution; preservation-layer principle was a refinement during E4 dialogue
- [B3 dynamic-research-expansion](architecture.md#b3--dynamic-research-expansion-infrastructure) — cache+freshness model; preservation extends this with archival semantics
- [A4 + B4 bitemporal lifecycle](architecture.md#a4--data-persistence--knowledge-model-storage) — preservation aligns with bitemporal discipline
- [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — preservation maintains trail integrity across time
- [Sweep #11 recipe sourcing](../11-recipe-sourcing/scope.md) — recipe attribution + provenance pipelines now extended with preservation status
- [Publication ambitions](publication-ambitions.md) — publication target reproducibility depends on preservation
