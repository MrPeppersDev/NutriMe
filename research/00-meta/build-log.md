# NutriMe — Build log

Running record of build sessions: what landed, where it lives, what is
left. Newest session first. Strategic context stays in
[roadmap.md](roadmap.md); this is the "what was done" trail.

## 2026-10-07/08 — audit remediation sessions (P0 → P1 → P2)

The 2026-10-06/07 audit queue, worked oldest-severity-first across
several budget-interrupted sessions. Everything below is on `main`.

### P0s (both audit passes) — all closed
- **Security exploit chain** (`898e31f`, closes #50): Host/Origin
  browser boundary (CSRF + DNS rebinding), SSRF guard re-checked on
  every redirect hop (`safe_urlopen`), vault path containment, XSS
  onclick→data-* sweep, generic 500s logging to `server-errors.log`,
  keychain writes via stdin. Exploit probes re-run live post-fix.
- **Data integrity** (`1caf726`): `db.transaction()` (BEGIN IMMEDIATE,
  nestable), race-free tenant bootstrap (4-way concurrent initialize
  verified), crash-safe per-migration commits, atomic vault writes.
- **Threaded server** (`346a814`): ThreadingHTTPServer + per-thread
  Application; WAL mode. /api/tonight answers in 7ms during a search.
- **Latest-plan bug** (`c6052dd`): five consumers read plans[-1] of a
  newest-first list — tonight/grocery/CLI/notification read the OLDEST
  plan. Regression tests verified failing pre-fix.
- **Consent enforcement** (`7cbe982`), **CLI condition gating**
  (`2479e1c`), **allergen shellfish gap + first live-vault vet**
  (`1a60be7`), **UTC/local plan-day math** (`951e074`, regression test
  pins a UTC-evening instant; suite green across 7 TZs).

### 2026-10-07 audit siblings (#53, #55-#58) — all closed
- #53 Windows UTF-8 (`506a0d8`); #55 expired perishables excluded from
  all cooking surfaces + "probably toss" strip (`a29814b`); #56
  shelf-life table rebuilt per the FDA cold-storage chart + LLM-tier
  raw-protein clamps (`a065ff2`); #57 FDA allergen-name synonyms +
  detector gap sweep, vault re-vetted, 342 recipes gained tags
  (`00591ad`); #58 condition registry fails CLOSED — unrecognized →
  gate, refuse-tier rows filled, negation + Roman numerals (`0d1e1c3`).

### #49 — plan reasons become a fixed vocabulary (`dc8e031`)
The planner model no longer writes display text: it picks a
`reason_code` (7 codes) and `render_reason()` builds the sentence from
corpus facts. Off-vocabulary codes degrade to "" at parse. The regex
layer stays as defense in depth and got the probe-table paraphrases.

### P1 UX (`bd39403`) + docs (#52 `c10ed5a`, #59 partial `280fba9`)
"We cooked this" on recipe detail (feedback ungated from plans);
mobile modals above the tab bar + 16px inputs; Escape no longer wedges
the member picker; honest failure states; per-slot unfilled reasons
shown; refusal banner on Plans; grocery "got it" → kitchen list with
lexicon-classified location/date; per-plan grocery link.
product-framing.md aligned to Block A v2. Sweep-07 Wolfson DOIs fixed
(Crossref-verified). #51 licensing closed by owner decision
(public-only sources + attribution = keep the corpus).

### P2 (`9989f03` + verification runs)
- **Meal-category inference** (vetting v3): title-based, fills EMPTY
  `meal_categories` only, `meal_categories_inferred: true` stamp; 314
  live recipes tagged; desserts can no longer reach dinner pools via
  main-by-exclusion. Savory-pie exceptions (pot/shepherd's/tamale...).
- **Crawler first run verified**: budgetbytes + simplyrecipes, 7
  recipes written with correct attribution + link-back frontmatter.
- **Planner live evidence**: real `plans generate` against qwen3:8b —
  2/2 dinner slots filled, reason codes rendered deterministically.

### In flight (parallel session, not yet merged)
Shared food-matching module (`foods/matching.py`), allergen "-free"/
vegan negation + plant-milk rewrites, inventory `match_name` column
(migration 0012), grocery netting via the shared matcher, allergen-chip
UI rework. Next migration number: 0013.

## 2026-10-06 — cloud session (direction-reset follow-through)

Work was split into one stacked PR per issue. Merge them in order; each
PR targets the one before it, and GitHub retargets to `main` as each
base branch is merged and deleted.

| # | Issue | Branch | PR | Status |
|---|---|---|---|---|
| 1 | #23 attribution gate | `claude/23-attribution-gate` | #35 | done; issue stays open as the gate for future surfaces |
| 2 | #29 per-member identity | `claude/29-members` | #36 | done (closes #29) |
| 3 | #30 constitutional layer | `claude/30-surface-rules` | #37 | pre-surface rules landed; future surfaces must route through `SurfaceGuard` |
| 4 | #31 vetting v2 | `claude/31-vetting-v2` | #38 | rule-based half done; local-LLM scoring waits on Ollama |
| 5 | #32 crawler | `claude/32-crawler` | #39 | crawler + CLI done; no sources enabled by default |
| 6 | #33 product UI | `claude/33-product-ui` | #40 | first full slice: app shell, adaptive home, reorient, plans, grocery, profile/consent, error surfaces |
| 7 | #34 self-host packaging | `claude/34-packaging` | #41 | backup/restore, doctor, installers (untested on real Windows/macOS), INSTALL.md |
| 8 | #32 follow-up: default sources + Pinterest top pins | `claude/32b-default-sources` | #42 | household decision: crawl major bot-permitting recipe sites + Pinterest top food pins |

### #23 — attribution on every web surface
- Tonight panel renders the credit line; `TestAttributionGate` covers search cards, detail, Tonight, page markup.
- Detail links only open `http(s)` source URLs; inline favicon; cycle copy made conditional.

### #29 — per-member identity
- Migration 0006: `member`, `intake_profile_v2`, `member_id` on screener responses; first start moves the legacy profile under "Me".
- Per-member profiles, screeners, feedback atoms (`subject_id`), consent (member row overrides household row for that member).
- Household constraints = union of active members' avoids/prefers (search + planner already consume them).
- Web picker ("Who's using this?", `X-NutriMe-Member` header); CLI `nutrime members …` + `--member`.
- The uncommitted #29 WIP on the MVP host is superseded — discard it.
- Follow-ups: constraint retraction (archived member / removed allergen); cooking ratings stay household-level.

### #30 — constitutional rules at the pre-surface boundary
- `surface_rules.py`: BannedContent (Rules 3/4 + harm) → block; EvidenceFloor (Rule 7) → block without Tier 1–3; ConsultProfessional (Rule 1) → adjacent annotation.
- Wired at the planner's reason text; findings audited as `surface_rule` events.
- L1 surface corpus + whole-snapshot false-positive sweep (0 banned-content hits / 2,218 recipes).

### #31 — vetting v2 (rule-based)
- Quarantine: page-chrome ingredients, pointer-only methods, roundup pages. Flags: thin/missing method, implausible quantity/yield/time, linked ingredients.
- Allergen reconcile (add-only, `allergens_original` kept); cross-source duplicates hidden (`duplicate_of`; household pins win).
- **To do on the host:** run `nutrime recipes vet` once on the live vault.

### #32 — corpus expansion crawler
- `recipes/crawl.py` + `nutrime recipes crawl`: robots.txt obeyed (unreadable robots ⇒ host skipped; `Crawl-delay` only slows us down), paced ≥ 1 s (default 5 s), SSRF-guarded, in-scope hosts/paths only, per-run page budget, resumable state (`crawl_state.json`), dry-run mode.
- Sitemaps, sitemap indexes (one level) and HTML index pages as seeds; schema.org JSON-LD via the existing adapter.
- New `web` collection ("Public web (crawled)") distinct from the household's pins; site name + URL in every credit line; pages already pinned are never crawled again.
- Nothing enabled by default — sites go in `<data_dir>/crawl_sources.toml` (`nutrime recipes crawl --example`), because ToS posture is a per-site household decision. Pinterest global top-pins not implemented (ToS unresolved).
- Live crawling could not be exercised from the cloud session (egress policy blocks recipe sites); covered by fake-site tests.

### #33 — product UI, first full slice
- One code path for plan generation (`plans/service.py`) shared by CLI and web; missing local model → plain setup message (cross-platform) instead of a crash.
- New APIs: plans list/detail/generate, reorient tonight (alternatives + swap, audited), per-member consent toggles, household constraints.
- Page becomes an app: Home / Recipes / Plans / Grocery / Profile; bottom tab bar on phones, tabs on desktop; deep links (`#plans`).
- Home adapts to time of day (C5 Q5.1); "Change tonight's meal" (C5 Q5.5) offers quick no-model alternatives within the avoid-list and swaps them into the plan.
- Grocery checklist (ticks kept per device), profile page with answers, household avoid/prefer list, privacy switches, rename/remove/add people.
- Every API failure now shows a plain message (toast or inline box) instead of failing silently.
- Not yet: notifications (C5 Q5.2), dedicated audit view (C5 Q5.4), inline "why this?" drill-in; grocery parser quirk seen in testing ("12 oz boneless" — food name truncated) is pre-existing.

### #34 — self-host packaging
- `nutrime backup` (one zip: consistent SQLite copies via the online backup API, vault, crawl config/state, manifest; safe while running) and `nutrime restore` (validates, refuses path escapes, needs `--force` over live data, safety backup first, then normal startup applies newer migrations).
- `nutrime doctor` + Profile → *System check*: Python, data folder, database integrity + pending updates, recipes + vetting freshness, household profiles, backup age, local model + downloaded model — each with a plain fix.
- Live-upgrade proof: a test upgrades a database left at every earlier migration level.
- `scripts/install-windows.ps1` (winget Ollama + uv, model pull, corpus seed, vet, first backup, Task Scheduler at sign-in, `-Uninstall`) and `scripts/install-macos.sh` (Homebrew, launchd agent, `--uninstall`). **Not executed** — the cloud container has neither OS; bash syntax-checked only.
- `INSTALL.md` (non-operator guide) linked from README.
- Not done: phone access over Wi-Fi (needs auth/transport, #12); signed installer/packaged app.

### #32 follow-up — default sources + Pinterest top pins (household decision)
- Decision (2026-10-06): crawl all the top food recipe sites that allow third-party bots (not NYT Cooking), plus Pinterest's top food pins.
- Bundled `recipes/default_crawl_sources.toml`: 35 recipe sites (major publishers, independent sites, cuisine specialists) + `pinterest_top`. NYT Cooking and paywalled ATK/Cook's Illustrated deliberately absent. "Allows bots" is decided live by each site's robots.txt on every run; disallowing sites are skipped and reported. A household `crawl_sources.toml` replaces the list; `enabled = false` drops an entry.
- Root seeds expand to the sitemaps robots.txt advertises (recipe sitemaps preferred).
- Pinterest as discovery: public food pages → pins' outbound links → recipe fetched from the original site; robots checked on Pinterest and each destination; collection "Pinterest top pins" (distinct from the household's own pins); credit names the site "(via Pinterest)". No robots bypass — the gallery-dl board path (which reads Pinterest's internal API, disallowed for generic crawlers) is not used for this. If Pinterest's robots.txt disallows NutriMe, the run reports it and fetches nothing from Pinterest. The seed URL (food-and-drink ideas page) is unverified from the cloud session.
- Crawl auto-vets new recipes; installers schedule a weekly crawl (Sunday 3 am).
- Not verified live (egress-blocked); fake-site tests cover robots sitemaps, Pinterest link extraction, destination robots, Pinterest-disallow, facet separation.

### Grocery parsing rebuild (flagged critical by the household)
- Measured first: every ingredient line in the snapshot (21,294) parsed and checked for empty foods, digits in foods, descriptor-only foods, compounds. Before: ~1,190 bad parses (e.g. "boneless, skinless chicken breasts" → food "boneless"; "2 & 1/2 tbsp" stored as qty 2 + name "& 1/2 tbsp olive oil"). After: ~140, nearly all unusable import junk (whole recipes pasted into one line, French text) or legitimate product names ("90% lean ground beef", "half and half").
- `grocery/parse.py` rebuilt as staged repair: quantity repair (continuations, units in the qty field, quantities/metric echoes in names, package sizes), balanced nested parentheticals (food recovered from parens when the name is empty), descriptor-aware comma joining, trailing/usage phrases to notes, head units ("pinch of"), alternatives with shared heads, compound splitting ("salt and pepper" → two lines; "each: rosemary and thyme"; "egg and 1 egg yolk"), prep/size words to notes while identity words stay, prose lines dropped, link markup and invisible characters cleaned.
- Aggregation: one line can yield several needs; water/ice never listed; "4 garlic cloves" merges with "garlic (2 cloves)"; plural normalization fixed (tomatoes/tomato, berries/berry, leaves/leaf).
- Display: kitchen fractions (1½, ⅓, ¾) and plural units ("cups").
- Regression gate `tests/test_grocery_corpus.py`: 50 hand-labelled real lines + whole-corpus invariants (every line parses, no descriptor-only foods, ≤10 empty foods all prose, stray numbers <0.5%).

### Periodic check-ins (genesis promise; roadmap vision item 6)
- `checkins.py` + migration 0007 (`checkin`, `checkin_schedule`, `intake_profile_history`). Per member; due 28 days after the last check-in (or the first profile), 14 during pregnancy/breastfeeding; member-adjustable (2/4/8/13 weeks); "not now" snoozes a week; never due before a first profile.
- A check-in revises the profile (previous version kept in history), retakes the screeners with the change from last time shown, records cooking confidence + weeknight time, and replaces the cuisines-to-try (which now boost ranking via cuisine tags, with country/adjective aliases).
- Derivation gained retraction: removed allergies/preferences retract their atoms, and household constraints nobody active supports any more (allergy removed, or the person archived) are retracted — closing the add-only constraint gap from #29.
- Web: Home card when due, check-in mode of the intake overlay (+ cooking/cuisine step and a "what changed" summary), Profile → Check-ins (next due, cadence, history). CLI: `nutrime checkin [--status] [--member]`.
- Verified in a headless phone browser end to end (weight change, allergy removal, cuisine pick → summary → avoid-list updated).

### UI completion + browser tests (#33)
- No browser pop-ups left: "We cooked it" (ease/enjoyment 1–5 buttons, minutes, then a used-up checklist), add/rename/remove person all use in-page forms (`formSheet`).
- "Why this?" on recipe details (C5 Q5.4 inline drill-in): what it uses from the kitchen, soon-to-expire items, preferences matched, cook history, new cuisine, planner's note, avoid/prefer list applied.
- Notifications (C5 Q5.2): bell with count; per-member switches (migration 0008 `member_setting`); defaults material-only (feedback window, check-in due, system warnings); practical nudges (use soon, nothing planned tomorrow, new recipes) available but off.
- Activity view (C5 Q5.4 dedicated audit view): model requests, privacy decisions, safety findings, swaps, check-ins, cooked meals, profile revisions — plain words, 7/30/90 days.
- `tests/e2e/test_browser.py` (Playwright, optional `e2e` group): phone-size layout (bottom tabs, no sideways scroll), intake → avoid-list, add person, search → why-this → credit, plan → allergy respected → reorient swap → cooked form → feel prompt → grocery tick survives reload, full check-in, privacy toggle, notifications, activity, lost-server error. 8 tests, no page errors.

### Environment notes
- Cloud container: no GPU/Ollama, recipe sites blocked by egress policy — local-model work (#7/#9, #31 scoring) and live crawls need the Windows host.
