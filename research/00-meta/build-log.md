# NutriMe — Build log

Running record of build sessions: what landed, where it lives, what is
left. Newest session first. Strategic context stays in
[roadmap.md](roadmap.md); this is the "what was done" trail.

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
| 7 | #34 self-host packaging | `claude/34-packaging` | see PR list | backup/restore, doctor, installers (untested on real Windows/macOS), INSTALL.md |

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

### Environment notes
- Cloud container: no GPU/Ollama, recipe sites blocked by egress policy — local-model work (#7/#9, #31 scoring) and live crawls need the Windows host.
