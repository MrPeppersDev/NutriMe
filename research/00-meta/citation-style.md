# NutriMe — Citation Style and Cross-Reference Conventions

> Every research output must cite its sources. This document defines how.

## Principles

1. **Every claim cites a source.** No assertion goes unsupported in a research doc.
2. **Citations link out, not just describe.** Always include the URL or DOI.
3. **Accessed-on dates** for web sources, since web content drifts.
4. **Aggregate sources project-wide** in [sources.md](sources.md) so we can see when one source is used across multiple sweeps and update accessed-on dates uniformly.
5. **Cross-reference both ways.** When sweep A cites a finding from sweep B, add the back-link in sweep B's doc too.

## Citation formats

### Authoritative bodies / standards documents

```
**[Body abbreviation]** ([Year]). *[Document title]* ([Version / edition if applicable]).
[Publishing organization]. [URL]. Accessed YYYY-MM-DD.
```

Example:

> **NASEM** (2005). *Dietary Reference Intakes for Energy, Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino Acids*. National Academies of Sciences, Engineering, and Medicine. https://nap.nationalacademies.org/catalog/10490. Accessed 2026-04-28.

### Peer-reviewed journals

```
[Last name, First initial.], [Last name, First initial.] ([Year]).
[Article title]. *[Journal name]*, [Volume]([Issue]), [pages]. [DOI URL].
```

Example:

> Phillips, S.M., Chevalier, S., & Leidy, H.J. (2016). Protein "requirements" beyond the RDA. *Applied Physiology, Nutrition, and Metabolism*, 41(5), 565–572. https://doi.org/10.1139/apnm-2015-0550

### Web sources / organizational pages

```
[Author or organization]. ([Year if known]). *[Page title]*. [URL]. Accessed YYYY-MM-DD.
```

### Datasets / APIs

```
[Dataset name] (v[version], [date]). [Maintaining organization]. [URL]. License: [license].
```

## Inline references

In prose, use markdown links: `[Phillips et al. 2016](https://doi.org/10.1139/apnm-2015-0550)`. The full citation belongs in the `## References` section at the bottom of each doc.

## Cross-references between docs

Use relative markdown links from the doc's own location:

- Within same folder: `[scope.md](scope.md)`
- To another sweep: `[sweep #5 scope](../05-personalized-nutrition-evidence/scope.md)`
- To meta docs: `[constitutional rules](../00-meta/constitutional-rules.md)`

When you add a cross-reference in doc A pointing to doc B, add the corresponding back-link in doc B's "Related" or "Cross-references" section.

## Web fetch tracking

When research uses web fetch, the fetched URL must be added to:

1. The doc's own `## References` section (with accessed-on date)
2. [00-meta/sources.md](sources.md) (master aggregator)

This way, if a URL gets cited in three sweeps, we see that in one place and can refresh accessed-on dates uniformly.

## Evidence tier tagging

Wherever a claim is made, tag it with an evidence tier from [evidence-tiers.md](evidence-tiers.md):

> Studies suggest that high-protein breakfast may improve satiety [Tier 2: Leidy et al. 2015 systematic review].

Tier tagging is mandatory for any claim about effect, mechanism, or recommendation.
