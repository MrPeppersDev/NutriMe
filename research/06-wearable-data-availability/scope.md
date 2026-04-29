# Sweep #6 — Wearable & Biometric Data — Availability, Access, Signal Quality

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Build a **comprehensive catalog** of biometric and health data sources available to NutriMe — consumer wearables, clinical-grade data (labs, imaging, prescription devices, doctor-portal data), open-source / DIY infrastructure, and the data formats / APIs / protocols used to access them. Distinct from [sweep #5 (personalized nutrition evidence)](../05-personalized-nutrition-evidence/scope.md) which asks whether we should *act on* a given signal — this sweep maps what data exists and how it's grabbed.

## Deliverable

An annotated reference catalog containing:

### Per source (consumer wearable, clinical device, lab, doctor portal, OSS aggregator):

- Name, manufacturer / maintainer
- Data types exposed (HR, HRV, sleep stages, RHR, training load, glucose, weight, body composition, lipids, A1c, etc.)
- Access modality (native API, webhook, OAuth, file export, FHIR, HL7, CSV, raw sensor)
- Format(s) (JSON schema, FHIR resource, CCDA, CSV, proprietary binary, etc.)
- Authentication / consent flow
- Rate limits, pricing, license / ToS
- Geographic availability (flagged when notably region-limited)
- Signal quality / validation literature (peer-reviewed)
- Notes on portability and data ownership

### Cross-cutting layers:

- **Aggregator platforms** — Apple HealthKit, Google Fit / Health Connect, Samsung Health, Health Auto Export, FHIR Patient Health Record APIs, OAuth-based health data hubs
- **Clinical / doctor-portal data ingestion** — patient access APIs (FHIR US Core, Apple Health Records, OpenNotes, Epic MyChart APIs), lab portal integration patterns, "request labs from your doctor through the app" patterns
- **Open-source / DIY ecosystem** — Home Assistant health integrations, Nightscout (DIY CGM), OpenAPS-adjacent projects, self-hosted health dashboards, HealthKit-Bridge, oh-my-fitness, openHAB, FOSS aggregation projects
- **Signal validation literature** — peer-reviewed studies of consumer wearables vs. gold-standard reference (Apple Watch HR vs. ECG, Whoop sleep staging vs. polysomnography, Oura skin temp vs. clinical, Fitbit step counts, etc.)
- **Emerging signals** at reference level — cuffless blood pressure (Aktiia), non-invasive glucose (research-stage), sweat analysis (Epicore Nimbl), breath analysis, continuous core temperature
- **Privacy / data-rights frameworks** — GDPR, HIPAA + HITECH, PIPL (China), Australian Privacy Principles, PIPEDA (Canada), at the level affecting what data can ethically and legally be used

This is a **comprehensive catalog**, not corpus build. Goes deep enough on availability + format that we can decide later what to implement now vs. pipeline.

## In scope

### Consumer wearables (representative — research surfaces the full set)

- Apple Watch (all generations supported by current HealthKit), Apple Health
- Garmin (Forerunner / Fenix / Venu lines), Garmin Connect
- Whoop (4.0, MG)
- Oura (gen 3, gen 4)
- Fitbit (Pixel Watch successors)
- Polar (Vantage, Grit, H10 chest strap)
- Coros (Pace, Apex, Vertix)
- Withings (smart scales, BP monitors, Sleep Analyzer, ScanWatch)
- Eight Sleep (Pod), other smart mattresses
- Peloton + connected fitness (Concept2, Zwift, Strava)
- Suunto, Amazfit, Wahoo, Garmin Tactix, Casio G-Shock smart variants

### Clinical-grade data sources (priority)

- Lab panels — LabCorp, Quest, Sonora Quest, regional and international equivalents
- Direct-to-consumer labs — Everlywell, LetsGetChecked, Function Health, Marek Health, InsideTracker
- Prescription CGM — Dexcom G7 / Stelo, Abbott Libre 3 / Lingo
- Imaging — DEXA scans (BodySpec, DexaFit), MRI body composition (AMRA), bone density
- Genetic — 23andMe, AncestryDNA, Nebula Genomics, Whole-Genome services
- Microbiome — Viome, ZOE microbiome panel, BIOHM, others
- Doctor-portal data — Epic MyChart, Cerner / Oracle Health, Athenahealth, Allscripts patient APIs
- Apple Health Records (US Core FHIR) — patient-mediated clinical record aggregation
- "Request labs from your doctor" patterns — order entry workflows, requisition forms, lab-by-mail kits

### Aggregator layer

- Apple HealthKit (iOS / watchOS / iPadOS) — broadest consumer health aggregator
- Google Fit / Health Connect (Android)
- Samsung Health
- Health Auto Export (third-party HealthKit → cloud bridge)
- FHIR Patient Health Record APIs (US Core, IPS for international)
- HL7 v2 (older clinical exchange standard)
- OAuth-based health data hubs (Validic, Human API, Terra)

### Open-source / DIY ecosystem (priority equal to commercial)

- Home Assistant + health integrations
- Nightscout (DIY CGM aggregation, started in T1D community)
- OpenAPS / Loop (DIY closed-loop insulin — relevant context, not directly used)
- Self-hosted health dashboards (Grafana + InfluxDB patterns, Wger, etc.)
- HealthKit-Bridge / HealthFit — exporting HealthKit to other systems
- oh-my-fitness, openHAB health integrations, OpenScale (smart scales)
- FOSS aggregation libraries (python-google-fit, gadgetbridge, etc.)
- Self-sovereign health data movements (Solid pods for health, NOSH, openEHR)

### Signal validation literature

Per [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), signal-quality claims must be backed by peer-reviewed validation. Cover:

- Apple Watch HR / ECG vs. clinical Holter
- Whoop sleep staging vs. PSG
- Oura sleep + temperature vs. clinical
- Fitbit step counts vs. accelerometer ground truth
- Smart-scale BIA vs. DEXA for body composition
- Wearable HRV vs. ECG-derived HRV
- CGM (consumer + prescription) accuracy vs. capillary / venous blood glucose
- Cuffless BP devices vs. cuff measurement

### Emerging signals (reference level)

- Cuffless / continuous BP (Aktiia, Valencell, others)
- Non-invasive glucose (research-stage; flag vendors making questionable claims)
- Sweat analysis (Epicore Nimbl, others)
- Breath analysis (volatile organic compound profiling)
- Continuous core temperature (CORE, others)
- Continuous lactate (research-stage)

### Privacy / data-rights frameworks

- GDPR (EU + UK adapted)
- HIPAA + HITECH (US clinical)
- PIPL (China)
- Australian Privacy Principles
- PIPEDA (Canada)
- Brazilian LGPD
- Israeli Privacy Protection Law
- Right-to-portability provisions per region

## Out of scope (with reasons)

- **"Should we act on signal X" evidence audit** — that's [sweep #5](../05-personalized-nutrition-evidence/scope.md). This sweep maps the data substrate; the evidence-to-act question is a sister sweep.
- **Tech stack / implementation choices** — deferred per project-wide rule
- **Building integrations** — research first, implement later

## Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md): primary US, EU, UK, AU, NZ, Canada, China, Japan, Korea, Israel, Russia. Opportunistic elsewhere. Region-locked devices and regional data-rights variations flagged but not the primary focus — the focus is the catalog of available data + formats.

## Open questions for the research

- For each consumer wearable: what data types, what API access, what formats, what license?
- For doctor-portal data: what is the realistic state of patient API access (Apple Health Records, Epic MyChart APIs, FHIR US Core adoption rates)? What does "request labs through the app" actually look like across major US EHR vendors?
- For OSS / DIY: what's the most active ecosystem? Where does the community converge on standards?
- What is the peer-reviewed validation literature on consumer wearable signal accuracy, and how does it differ from vendor-published validation?
- What aggregators provide the broadest cross-device normalization with the cleanest data licensing?
- What emerging signal sources have plausible 1–3 year horizons for becoming real data sources?

## Cross-references

- Sister sweep to [sweep #5 (personalized nutrition evidence)](../05-personalized-nutrition-evidence/scope.md) — #6 = data substrate, #5 = should-we-act-on-it
- Bound by [Constitutional Rule 6 (health data stays local)](../00-meta/constitutional-rules.md#rule-6--health-data-stays-local-where-possible)
- Bound by [Constitutional Rule 8 (epistemic trail)](../00-meta/constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — clinical data interpretation will require provenance + reasoning + verification trails
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor) — signal validation claims must be peer-reviewed
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary research scope
- See [epistemic-trail.md](../00-meta/epistemic-trail.md) for how cross-referenced clinical data gets surfaced

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
