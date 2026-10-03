# Sweep #16 — Mealie code-level pattern study (6.1 entry material)

**Executed 2026-10-04** against a shallow clone of `mealie-recipes/mealie` (AGPL-3.0).
Prior classification stands: **prior art, ideas only — no code reuse** (AGPL vs our
Apache-2.0; see stage3-plan step 4 source table). Everything below is mechanism-level
findings to reimplement independently in stdlib. File refs point into the Mealie tree
as evidence for the reader, not as copy targets.

## Why now

6.1 (grocery list + export) opens next and its hardest sub-problems — ingredient
parsing, line merging, unit consolidation, pantry netting — are exactly what Mealie
has shipped for years. Sweep #13 flagged Mealie/Tandoor/Grocy at reference level;
this is the deferred code-level read for Mealie.

## 1. Ingredient parsing

- Three interchangeable parser backends (brute regex / CRF NLP / LLM) behind ONE
  output shape: `{quantity, unit, food, note, confidence-per-field}`. Downstream
  never knows which parser ran. **Adopt the interface split**: ship a stdlib brute
  parser for 6.1; an LLM parser can slot in later without touching callers.
- Brute parser mechanics worth mirroring (all stdlib: `fractions`, `re`,
  `unicodedata`): leading-digit/fraction scan incl. unicode vulgar fractions and
  mixed numbers ("1 1/2"); **move parenthetical content to end before tokenizing**
  ("1L (500ml) Water"); first comma splits food from note ("onion, diced");
  trailing-asterisk footnote strip. Unit detection consults the known-unit
  vocabulary to find the qty/unit/food boundary — a dictionary-assisted tokenizer,
  not pure regex.
- Matching: normalize once (accent-strip → punctuation→space → lowercase), then
  literal dict lookup, then fuzzy fallback with **per-field thresholds** (their
  hand-tuned values: food 85, unit 70, shopping-food 80 on a 0-100 ratio) — units
  tolerate looser matching than foods ("onion" must not merge with "green onion").
- Self-correcting re-match: if unit AND food both failed to match, retry
  `"{unit} {food}"` as a single food — catches "bay leaf" mis-split as unit=bay.
- LLM-parser confidence idea: **cross-check the smart parse against the dumb
  regex parse**; agreement is the confidence signal. Never trust model
  self-reported confidence. (Direct fit for our vision-extraction stage on #24.)

## 2. Shopping-list aggregation (the 6.1 core)

- **Merge-eligibility gate**, not general unit conversion: two lines merge only if
  food matches exactly (matched-food FK; free text requires exact note equality)
  AND units are identical or both carry a curated `standard_quantity/standard_unit`
  pair in the same dimension. **"2 cans" vs "400 g" never merges — two honest
  lines beat one wrong conversion.**
- Conversion table is tiny and hand-curated: ~13 of their 24 units have a
  standardization pair (tbsp→0.5 fl oz, gallon→16 cup, mg→0.001 g…); can / bunch /
  pinch / clove / head / sprig / serving are **deliberately non-convertible**.
  The mapping is a pure function of normalized unit name. Resist building a pint
  equivalent.
- Display heuristic after merge: render in the larger of the two input units when
  result ≥ 1, else the smaller ("2.5 cups", never "0.02 gallons").
- **oz/fl-oz disambiguation hardcoded**: recipe authors write "oz" meaning fluid
  ounces for liquids; when an ounce meets a volume unit, treat it as fl oz.
- **Provenance ledger per aggregated line**: every line keeps
  (recipe_id, scale) references so removing a recipe from the plan subtracts
  exactly its contribution from the merged line instead of deleting the line.
  This is the idempotent add/remove mechanism — adopt structurally.
- Checked/purchased items are **frozen out of all aggregation** — a hard boundary,
  not a UI flag.
- **Pantry netting gap**: Mealie's "on hand" is a boolean per-household food flag
  (salt, oil) that suppresses the line entirely — no quantity-aware netting
  anywhere. Our 6.1 presence-based inventory netting matches their state of the
  art; quantity-aware netting would exceed it and is genuinely new design work.

## 3. Scraper robustness (sanity-check for our jsonld.py)

- Fallback ladder: recipe-scrapers lib (schema.org wild mode) → LLM page-read →
  Open Graph stub that still returns title+image rather than nothing. Each
  strategy try/except-wrapped; any exception falls through to the next.
- Post-parse validity check: accept only if ingredients OR instructions non-empty.
  (Ours: jsonld extract → skip-and-report. Adding an OG-stub fallback is a cheap
  future resilience step; the validity check we effectively have.)
- Their `cleaner.py` edge-case catalogue = field guide to malformed schema.org in
  the wild. Cases our jsonld.py does NOT yet handle, as a punch list for when
  real-world pages misbehave: image as 5 shapes; instructions as JSON-stringified
  arrays; dicts keyed "0"/"1" (0- AND 1-indexed); HowToSection using `item` for
  `itemListElement`; bare-dict section; capitalized `Name` key; HowToStep.name as
  ellipsis-truncated copy of .text (drop heading if .text startswith it);
  double-escaped HTML needing clean-until-stable loop; European comma decimals;
  servings vs yield as separate concepts.
- Fetch layer: body-sniffing for bot-challenge markers even on HTTP 200;
  jittered backoff honoring Retry-After; per-attempt timeout PLUS overall
  wall-clock budget; **SSRF protection** (resolve → reject private/loopback/CGNAT
  ranges → pin connection to validated IP) — stdlib-implementable
  (`socket.getaddrinfo` + `ipaddress`) and relevant because our web UI accepts
  arbitrary user-pasted URLs. Their TLS-fingerprint rotation / headless-browser
  escalation: **skip** — disproportionate for a local-first household tool.

## 4. Seed data shape (and the corpus answer)

- **Mealie ships ZERO recipes.** Confirmed in-tree and across the
  `mealie-recipes` org repos: seed data is 24 units + 580 foods in 20
  aisle-category groups (per-locale JSON, name+plural only — no densities, no
  nutrition). It's a manager you bring recipes to; there is nothing to ingest
  corpus-wise, and AGPL would bar bundling their seed JSONs anyway. Our own
  ~20-unit + ~few-hundred-food seed lists are an afternoon's authoring.
- Shape worth mirroring: aisle-category label on foods drives shopping-list
  grouping — our 6.1 export wants the same axis.

## Verdict for 6.1 entry

Adopt: parser interface split + brute tokenizer; normalize-once + per-field fuzzy
thresholds; merge-eligibility gate with curated ~15-pair conversion table;
oz/fl-oz rule; provenance ledger; frozen checked-lines; aisle grouping; SSRF guard
on user-pasted URLs. Defer: cleaner.py punch list (apply as real-world breakage
appears); OG-stub fallback. Skip: pint algebra, fuzzy/ML deps, anti-bot
infrastructure, multi-locale seeds. Tandoor/Grocy code reads deferred until a 6.1
problem demands a second reference.
