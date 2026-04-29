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

> **Epistemic note (per Rule 8).** This catalog was assembled in a session in which live `WebSearch` and `WebFetch` were unavailable. URLs are canonical documentation / DOI endpoints known at the assistant's training cutoff (January 2026). Accessed-on dates of `2026-04-28` reflect the date the catalog was assembled, not a fresh fetch — a follow-up pass should re-fetch each URL to confirm versions, current rate limits, pricing, and ToS, then update accessed-on dates. API surface details (endpoints, scopes, rate limits) drift quickly; treat them as orienting rather than authoritative until re-verified. Peer-reviewed validation citations are stable and were drawn from indexed literature.

### 1. Consumer wearables — capability matrix

#### 1.1 Apple Watch + HealthKit (Apple)

- **Data types exposed (HealthKit):** heart rate, resting HR, walking HR, HRV (SDNN), VO2 max, ECG (single-lead, classifies sinus / AFib / inconclusive), blood oxygen (SpO2 — feature paused for new US units 2024+ pending patent litigation), respiratory rate, wrist temperature (Series 8+, Ultra), sleep stages (awake / REM / core / deep, watchOS 9+), workouts, step count, distance, active energy, stand hours, mindful minutes, mobility (gait, walking steadiness), audio exposure, menstrual cycle inputs + cycle deviations, fall detection, irregular rhythm notifications. Read access also to `HKClinicalRecord` (FHIR R4) for connected health systems via Apple Health Records.
- **Access modality:** native iOS / watchOS / iPadOS framework (`HealthKit` Swift / Obj-C). Only on-device — no first-party cloud REST API. Cross-device sync is iCloud-encrypted between user's own devices.
- **Format(s):** Apple-internal SQLite store on device; user-initiated XML export via Health app ("Export All Health Data"), zipped XML + CDA (clinical) + workout GPX. Programmatic access returns `HKSample` subclasses (`HKQuantitySample`, `HKCategorySample`, `HKWorkout`, `HKHeartbeatSeriesSample`, `HKElectrocardiogram`, `HKClinicalRecord` as FHIR JSON for clinical records).
- **Authentication / consent:** per-data-type read/write authorization sheet shown on first request; user can revoke per type in Settings. Apple does not see what the app reads (privacy-by-design).
- **Rate limits / pricing / license:** no API rate limit (local). Apple Developer Program membership required to ship apps ($99/yr USD). App Store Review enforces HealthKit guidelines; HealthKit data may not be sold or used for advertising.
- **Geographic notes:** ECG, SpO2, AFib history, irregular rhythm, period prediction availability varies by region (notably ECG / SpO2 not initially available in Russia, China; SpO2 paused in US-sold units 2024+ for Series 9/10/Ultra 2 due to Masimo patent dispute).
- **Local-only by default (Rule 6 friendly):** raw health data stays on device; cloud sync is end-to-end encrypted iCloud only. No server-side processing required.
- **Validation literature:** see §5 below.

#### 1.2 Garmin (Forerunner / Fenix / Venu / Tactix / Epix / Vivoactive lines)

- **Data types:** HR (continuous + resting), HRV (overnight, "HRV Status" 7/28-day baseline), Body Battery (Firstbeat-derived energy estimate), stress (Firstbeat HRV-based), sleep stages + sleep score, Pulse Ox, respiration, skin temperature trend (newer Fenix 7/8, Epix), training load + acute load, training status, VO2 max, recovery time, performance condition, race predictor, running power (native on Fenix 7+/Forerunner 965+), running dynamics, cycling power (ANT+/BLE sensors), GPS tracks, FIT files, women's health cycle, hydration, body composition (Index S2 scale, BIA), blood pressure (Index BPM in select markets).
- **Access modality:** **Garmin Health API** (B2B partner program — application + commercial review required); **Garmin Connect IQ** (on-device app SDK, no cloud); **FIT file** export per activity from Garmin Connect web; third-party scrapers (e.g., `python-garminconnect`) against the consumer Connect endpoints (unofficial, ToS-grey).
- **Format(s):** Health API returns JSON (daily summaries, epoch summaries, sleep summaries, stress, HRV, Pulse Ox, body comp, user metrics); ANT+/BLE FIT binary; TCX / GPX export; activity FIT.
- **Authentication / consent:** OAuth 1.0a (Health API). Per-user partner consent.
- **Rate limits / pricing / license:** Health API requires partner agreement; per-user pricing tier (historically $0.30–$1.00/user/yr commercial reports — varies, request per partner). Push (webhook-style) "ping" notifications and pull endpoints. Data redistribution restricted; no resale.
- **Geographic notes:** Connect IQ + Connect cloud global; Index BPM blood-pressure scale launched select EU + US markets only.
- **Local capability:** FIT export local; Health API requires Garmin cloud as intermediary.
- **Validation literature:** Firstbeat-derived metrics have peer-reviewed validation for VO2 max + HR (Tier 3); HRV / Body Battery / stress less independently validated.

#### 1.3 Whoop (4.0, MG)

- **Data types:** continuous HR, HRV (RMSSD), respiratory rate, skin temperature (Whoop 4.0+), SpO2 (4.0+), sleep stages + duration + disturbances + sleep performance, recovery score (composite of HRV + RHR + sleep), strain (cardiovascular load metric, Banister-derived), workouts, "Journal" qualitative behavior tracking, menstrual cycle (4.0+), Whoop Body (apparel-integrated electrodes for ECG-grade HR — MG model).
- **Access modality:** **Whoop Developer API v2** (OAuth 2.0). Endpoints for cycles, recovery, sleep, workouts, body measurements, profile.
- **Format(s):** JSON.
- **Authentication / consent:** OAuth 2.0; scopes `read:recovery`, `read:cycles`, `read:sleep`, `read:workout`, `read:profile`, `read:body_measurement`, `offline`.
- **Rate limits / pricing / license:** Whoop subscription required for the device (no separate API fee for personal-use developer apps as of v2 launch). Rate limits documented per endpoint (commonly 100 req/min). Approval gate exists for production-tier scopes.
- **Geographic notes:** Whoop ships globally; clinical-grade BP / glucose features not present.
- **Local capability:** all data flows through Whoop cloud — local-only ingestion not available.
- **Validation literature:** see §5.

#### 1.4 Oura Ring (Gen 3, Gen 4)

- **Data types:** HR (5-min resolution overnight + spot daytime), HRV (RMSSD overnight), respiratory rate, SpO2 (Gen 3+), skin / finger temperature (deviation from baseline), sleep stages + sleep score, readiness score, activity score, daily movement, women's cycle prediction (Natural Cycles partnership / Oura Cycles), tags, workouts (manual + auto-detected on Gen 4).
- **Access modality:** **Oura API v2** (OAuth 2.0, REST, JSON). Personal Access Tokens for own-data developer use.
- **Format(s):** JSON; GraphQL not offered as of v2.
- **Rate limits / pricing / license:** Free tier for personal / non-commercial; commercial use requires partner agreement. 5,000 req/day documented historical default.
- **Geographic notes:** ships globally; subscription model (post-2021 hardware requires monthly subscription for full features).
- **Local capability:** ring streams to phone via BLE then Oura cloud; no local-only path.
- **Validation literature:** see §5.

#### 1.5 Fitbit (Google) / Pixel Watch

- **Data types:** HR, HRV, RHR, sleep stages + sleep score, SpO2, skin temperature deviation, breathing rate, ECG (Sense 2, Charge 6, Pixel Watch 2/3), AFib detection, EDA (stress), step count, distance, active zone minutes, weight (Aria scales), continuous glucose (in regions where supported via partners), women's health cycle.
- **Access modality:** **Fitbit Web API** (OAuth 2.0 PKCE). Migration in progress: post-Fitbit/Google merger, Pixel Watch data flows via **Android Health Connect** rather than Fitbit Web API (Fitbit Web API remains for legacy devices and existing apps). Fitbit announced reduced Web API roadmap and gradual sunset for some endpoints.
- **Format(s):** JSON; intraday endpoints (1 sec / 1 min HR, steps) require explicit "Personal" application approval.
- **Authentication / consent:** OAuth 2.0 with scopes (`activity`, `heartrate`, `sleep`, `nutrition`, `weight`, `profile`, `settings`, `social`, `oxygen_saturation`, `respiratory_rate`, `temperature`, `cardio_fitness`, `electrocardiogram`).
- **Rate limits / pricing / license:** 150 req/hour/user default; intraday access requires manual approval. Free for personal/dev; commercial requires terms acceptance.
- **Geographic notes:** ECG, AFib, SpO2 region-gated by clearance (e.g., MDR in EU).
- **Local capability:** Health Connect path supports on-device storage (Android-only); Fitbit Web API requires cloud round-trip.
- **Validation literature:** see §5.

#### 1.6 Polar (Vantage V3, Grit X2 Pro, H10 chest strap, Verity Sense, Ignite)

- **Data types:** HR (chest-strap-grade with H10), HRV, RR-intervals (raw beat-to-beat — H10 streams via BLE GATT Heart Rate Service + Polar's BLE PMD service for ECG and accelerometer), Nightly Recharge (autonomic + sleep), sleep stages, training load pro, recovery pro, FuelWise, running power, GPS.
- **Access modality:** **Polar AccessLink API** (OAuth 2.0, REST/JSON) for cloud-stored data; **Polar SDK** (BLE PMD) for raw on-device sensor streams from H10 / Verity Sense / OH1.
- **Format(s):** JSON (AccessLink); raw BLE binary frames decoded via Polar SDK; TCX/GPX export from Polar Flow.
- **Rate limits / pricing / license:** AccessLink free for developers; partner approval required for prod. SDK MIT-licensed.
- **Local capability:** Polar SDK enables direct BLE → device, no cloud required (notable for HRV research use).
- **Validation literature:** H10 widely used as reference standard in HRV / HR validation studies.

#### 1.7 Coros (Pace 3, Apex 2 Pro, Vertix 2/2S)

- **Data types:** HR, HRV, sleep, stress, training load, GPS, running power (native), skin temperature (newer Vertix 2S).
- **Access modality:** **COROS Open API** (OAuth 2.0, partner application). FIT file export per activity. Coros Training Hub web export.
- **Format(s):** JSON, FIT.
- **Rate limits / pricing / license:** partner-approval gated; intended for commercial integrations (TrainingPeaks, Strava, etc.).
- **Local capability:** FIT files local once exported.

#### 1.8 Withings (Body+, Body Scan, BPM Connect/Core, Sleep Analyzer mat, ScanWatch, ScanWatch 2)

- **Data types:** weight, body composition (BIA — fat %, muscle, bone, water; Body Scan adds segmental composition + 6-lead ECG via handles + nerve activity proxy + vascular age), blood pressure (BPM Connect / Core, FDA-cleared, EU MDR), sleep stages (Sleep Analyzer under-mattress ballistocardiograph; ScanWatch wrist-based), HR, SpO2, ECG (single-lead, ScanWatch family — FDA cleared / CE), temperature, activity.
- **Access modality:** **Withings Public Cloud API** (OAuth 2.0). Webhook notifications.
- **Format(s):** JSON.
- **Rate limits / pricing / license:** developer access free; partner agreement for production. Some clinical SDKs (Withings RPM) commercial.
- **Geographic notes:** medical claims region-gated (CE / FDA / Health Canada). Russia distribution limited post-2022.
- **Validation literature:** Sleep Analyzer validated against PSG (Edouard 2021); BPM cleared as Class IIa.

#### 1.9 Eight Sleep (Pod 3, Pod 4)

- **Data types:** sleep stages (mattress-cover sensors), HR, HRV, respiratory rate, bed temperature (controlled per side), tosses & turns, snoring (Pod 4).
- **Access modality:** **no official public API**. Community reverse-engineered Python clients (e.g., `pyEight`, used by Home Assistant integration) hit the consumer mobile app endpoints — undocumented, ToS-grey, breakage risk on every app update.
- **Format(s):** JSON over consumer endpoints.
- **Rate limits / pricing / license:** subscription required for full features ("Autopilot"). No partner program publicly advertised as of training cutoff.
- **Local capability:** none — cloud-only.
- **Validation literature:** limited independent peer-reviewed validation; vendor whitepaper claims (Tier 4).

#### 1.10 Wahoo (Tickr, Elemnt Bolt/Roam/Rival, Kickr trainer ecosystem)

- **Data types:** HR (Tickr chest), running dynamics (Tickr Run/X), GPS, power (cycling), cadence, indoor trainer wattage, structured workouts.
- **Access modality:** **Wahoo Cloud API** (OAuth 2.0, partner). Direct BLE/ANT+ for sensors. FIT export.
- **Format(s):** JSON, FIT.
- **Rate limits / pricing / license:** partner-gated.
- **Local capability:** sensors stream BLE direct to apps without Wahoo cloud.

#### 1.11 Suunto (Race, Vertical, 9 Peak Pro, 7)

- **Data types:** HR, HRV, sleep, stress (Firstbeat-derived on most models), GPS, training load, recovery, oxygen saturation (select).
- **Access modality:** **Suunto API** (formerly Movescount, now via SuuntoApp / partner program). Strava sync widely used as alt path.
- **Format(s):** JSON, FIT, GPX.
- **Local capability:** FIT export.

#### 1.12 Amazfit / Zepp Health (T-Rex, GTR, Cheetah, Helio Ring/Strap)

- **Data types:** HR, HRV, sleep, SpO2, stress, body temperature (select), Zepp Aura (sleep AI), readiness, ECG (select). Uses BioCharge / BioTracker PPG sensors.
- **Access modality:** **Zepp OS SDK** (mini-apps on device); **Zepp Open Platform** API (partner program, less mature than Garmin/Fitbit). Some unofficial scrapers.
- **Format(s):** JSON.
- **Geographic notes:** wide global distribution; data residency historically split between China-region servers and global servers (relevant under PIPL).

#### 1.13 Other / opportunistic

- **Casio G-Shock G-Squad / GBD-H2000:** HR, GPS; Casio Health Planet app; limited public API. 
- **Polar Verity Sense / OH1:** optical HR armband, BLE direct, supported by most fitness apps.
- **Movano Evie Ring:** women-focused ring; limited API at training cutoff.
- **Ultrahuman Ring Air, Ringconn, Circular Ring:** Oura competitors; partner APIs nascent or absent.
- **Samsung Galaxy Watch (Watch6/7/Ultra):** continuous HR, ECG, BP (cuff calibrated, region-gated), body composition (BIA), sleep stages, skin temperature. Data via **Samsung Health SDK** + **Health Connect** on Android.
- **Connected fitness (Peloton, Concept2 ErgData, Zwift, Strava, TrainerRoad):** Strava acts as de facto aggregator (Strava API v3 OAuth 2.0); Peloton has unofficial API only; Concept2 LogBook API exists; Zwift has no official public API but exports FIT.

### 2. Clinical-grade data sources (priority)

#### 2.1 Reference / consumer-clinical lab providers

- **LabCorp (US):** **LabCorp Patient API / Patient portal** (consumer-mediated). Direct-to-consumer ordering via LabCorp OnDemand. Results delivered in HL7 v2 to ordering providers; patient PDF + structured FHIR via patient portal (FHIR R4, US Core profiles).
- **Quest Diagnostics (US):** **MyQuest** patient portal; **Quest Diagnostics FHIR API** (US Core); Quest also operates Quanum EHR. Consumer DTC via QuestDirect.
- **Sonora Quest (Arizona joint venture), regional networks (BioReference, Mayo Clinic Labs reference, ARUP):** all increasingly expose FHIR R4 patient APIs under ONC Cures Act information-blocking rule (US, effective 2021–2023).
- **International:** Synlab (Europe), Sonic Healthcare (AU/NZ/US/EU), Eurofins, Unilabs — patient portals vary; FHIR adoption uneven outside US. NHS uses **NHS App** + **GP Connect FHIR API** + Patient Online (UK). Australia uses **My Health Record** (national PHR with FHIR + CDA).
- **Format(s):** HL7 v2 ORU (provider workflow), FHIR R4 `DiagnosticReport` + `Observation` + `Specimen` (patient access), CSV / PDF (patient self-export).

#### 2.2 Direct-to-consumer (DTC) labs

- **Everlywell:** finger-prick / saliva / urine kits; results in app + PDF; **no public API** for third-party ingestion as of training cutoff.
- **LetsGetChecked:** kit + telehealth model; partner API for enterprise / payer integrations; no consumer dev API.
- **Function Health:** subscription panel ($499/yr historic) covering ~100 biomarkers; results in app + PDF; **no public consumer API** at training cutoff.
- **InsideTracker:** lab + DNA + algorithmic recommendations; partner API for enterprise; consumer can request CSV export.
- **Marek Health:** concierge labs (Quest reference panels); PDF results.
- **Thorne (Onegevity, Wellness Tests):** PDF + portal.
- **ZOE microbiome / blood-fat / glucose home study:** mobile app, no public API.
- **Viome (Gut Intelligence, Full Body Intelligence):** RNA-based microbiome metatranscriptomics; mobile app; no public API.
- **GenoPalate, DNAfit, Nutrigenomix:** nutrigenomic panels; PDF + app; no public API.
- **AncestryDNA, 23andMe, MyHeritage, Living DNA:** raw genotype download (CSV / TXT) supported (Rule-6-friendly: download once, process locally with `bcftools` / Promethease / PRSice locally).
- **Nebula Genomics, Dante Labs, Sequencing.com, Veritas:** WGS providers; deliver FASTQ / BAM / VCF; large file portability. Format = standard bioinformatics (FASTQ, BAM, gVCF, VCF).
- **Microbiome (Viome, ZOE, BIOHM, Thryve / Ombre, uBiome legacy, American Gut / The Microsetta Initiative):** raw FASTQ rarely exposed (Microsetta / open citizen-science projects do); commercial reports are PDFs + interpretation tied to vendor.

#### 2.3 Prescription continuous glucose monitors (CGMs)

- **Dexcom G7 / G6:** **Dexcom API** (partner OAuth 2.0; "Dexcom Developer Portal"); ~3-hour-delayed data for partners (real-time access requires special agreement, e.g., Dexcom Share for caregiver); **Dexcom Stelo** (OTC CGM in US, launched 2024) uses the Dexcom companion app + API path for partners.
- **Abbott FreeStyle Libre 2 / Libre 3 / Lingo (consumer non-prescription wellness CGM in US/UK):** **LibreView** cloud (clinician/patient portal); **LibreLinkUp** for caregivers; partner / consumer APIs limited; community projects: **xDrip+** (Android, Bluetooth direct from Libre 2/3), **Diabox**, **Juggluco** for direct sensor reads.
- **Eversense E3 (Senseonics, implantable 180-day CGM):** Eversense DMS web; no public consumer API.
- **Medtronic Guardian 4 / Simplera:** CareLink API (partner-only).
- **Levels, NutriSense, Signos, Veri, January AI, Nutrisense, ZOE CGM:** wellness / coaching layers on top of Libre + Dexcom; their app is the access point; raw underlying data accessible via Nightscout/xDrip in the DIY ecosystem.
- **Format(s):** JSON over partner APIs; FHIR `Observation` for clinical interfaces; CSV from LibreView / Clarity export; raw NFC + BLE for community decoders.
- **Geographic notes:** Stelo OTC US-only at launch; Lingo first in UK then US; Libre 3 widely available; Dexcom G7 US/EU/UK/CA/AU/NZ/JP.

#### 2.4 Imaging / body composition / bone density

- **DEXA (DXA):** clinical bone density + body comp gold-standard. Consumer providers: **BodySpec** (US, mobile clinics), **DexaFit** (US franchise), **Fitnescity** (booking aggregator), **Dexa Body** (UK), local hospital radiology elsewhere. Reports as PDF; structured data not standardized for consumer export.
- **MRI body composition:** **AMRA Researcher** (Sweden) — clinical-grade MRI body comp; provider-facing; consumer can request via partner clinics.
- **3D body scanners (Styku, Fit3D, Naked Labs (defunct), Visbody):** circumference + estimated body comp; gym/clinic-bound; CSV/PDF exports.
- **Bone density (peripheral DEXA, ultrasound BMD, REMS via EchoLight Echolight):** specialty clinics.
- **Coronary calcium scoring (cardiac CT):** hospital-ordered; report PDF + DICOM; no consumer API.
- **VO2 max metabolic carts (PNOE, KORR CardioCoach, COSMED):** vendor-specific cloud; CSV export.
- **Format(s):** PDF reports dominate; DICOM for raw imaging; FHIR `ImagingStudy` resource for orchestrated environments.

#### 2.5 Genomics

- **23andMe Health + Ancestry:** raw download (`.txt`, ~600k SNPs) — Rule-6-friendly local re-analysis with **Promethease** (now defunct), **Genetic Lifehacks**, **SelfDecode**, or open-source `snpsift`/`bcftools` chains.
- **AncestryDNA:** raw download (`.txt` / `.csv`).
- **MyHeritage / Living DNA / FamilyTreeDNA:** raw download.
- **Nebula / Dante / Sequencing.com:** WGS — FASTQ/BAM/VCF, hundreds of GB; portable.
- **Format(s):** vendor-specific genotype TSV (chr, position, rsID, allele1, allele2); standard bioinformatics formats (FASTQ, BAM, gVCF, VCF) for WGS.

#### 2.6 Microbiome

- **Viome:** RNA metatranscriptomics; PDF + app; vendor-locked recommendations.
- **ZOE:** microbiome (16S) + CGM + blood-lipid postprandial; app-locked.
- **BIOHM, Thryve / Ombre, Sun Genomics (Floré):** 16S rRNA; PDF + app.
- **Microsetta Initiative / American Gut:** academic citizen-science; raw FASTQ + open data.
- **Format(s):** FASTQ raw rare from commercial; QIIME2 / BIOM open formats; vendor PDFs.

#### 2.7 Doctor-portal patient APIs (US-centric, then global)

- **Apple Health Records:** patient-mediated FHIR aggregation; user signs into participating provider via OAuth in iOS Health app; records appear as `HKClinicalRecord` of type `Allergies`, `Conditions`, `Immunizations`, `LabResults`, `Medications`, `Procedures`, `Vitals`. As of training cutoff: 1000+ US health systems, expanding UK (NHS, select trusts), Canada (select), Australia, plus IPS exchange in EU pilots.
- **Epic MyChart (FHIR R4 patient access):** Epic exposes US Core FHIR endpoints per ONC Cures Act §170.315(g)(10); patient-mediated OAuth via SMART on FHIR; Epic Open.Epic developer portal lists endpoints.
- **Oracle Health (Cerner Millennium successor) / HealtheLife portal:** SMART on FHIR R4 endpoints; "Code" developer portal (code.cerner.com → now Oracle Health).
- **Athenahealth / athenaPatient:** FHIR R4 Patient Access API; developer portal.
- **eClinicalWorks (eCW), Allscripts/Veradigm, NextGen, Greenway, Practice Fusion:** all certified for ONC Cures Act, expose FHIR R4 patient access.
- **CommonWell / Carequality / TEFCA QHINs:** national interop networks, increasingly accessible to patient-mediated apps via TEFCA's Individual Access Services rollout (2024–2026).
- **NHS App (UK) + GP Connect:** patient access to GP-held records (FHIR STU3 historically, R4 for newer profiles).
- **My Health Record (Australia):** national PHR; **Healthi**, **HealthEngine** for patient access; FHIR R4 + CDA.
- **Health Canada (provincial):** Ontario eHealth, Alberta MyHealthRecords, etc. — fragmented; no national patient API equivalent.
- **France:** **Mon Espace Santé** (DMP successor); FHIR rollout per "Doctrine du Numérique en Santé."
- **Germany:** **ePA** (elektronische Patientenakte, mandatory 2025 opt-out model); gematik FHIR profiles.
- **Israel:** Clalit, Maccabi, Meuhedet, Leumit HMOs each operate patient apps; FHIR adoption via Ministry of Health's "Eitan" project.
- **Korea:** **My HealthWay** (의료마이데이터); FHIR-based national patient access launched 2023.
- **Japan:** **PHR** strategy under MHLW; **Maina Portal** + insurer apps; FHIR pilot.
- **China:** highly fragmented; major hospitals have WeChat-mini-program portals; PIPL governs cross-border transfer.
- **"Request labs from doctor" pattern:** in-app flow typically links out to (a) patient portal message-the-doctor; (b) DTC kit purchase if uninsured route is preferred; (c) requisition PDF the user prints and brings to a lab draw station (Quest / LabCorp accept paper requisitions from licensed providers in many states; some allow patient self-pay direct order).

### 3. Aggregator platforms

- **Apple HealthKit** (above §1.1) — broadest consumer aggregator; on-device.
- **Google Health Connect** (Android 14+, replaces Google Fit REST API which deprecated 2024 with full sunset 2025-06-30): on-device data store; client SDK for read/write per data type; permissions per type via Android system UI; over 50 supported data types incl. nutrition, hydration, exercise, sleep, vitals.
- **Samsung Health SDK** (Galaxy Watch / phones) + Health Connect bridge: on-device + Samsung cloud; partner-gated SDK.
- **Health Auto Export (iOS app, Lybron Sullivan):** third-party HealthKit → JSON / CSV / REST webhook bridge; Rule-6-friendly because user controls destination; commercial app ($).
- **Health Sync (Android, third-party):** Health Connect / Google Fit / Samsung Health / Garmin / Fitbit / Strava interop bridge ($).
- **OAuth health hubs / aggregator-as-a-service (commercial):**
  - **Terra (`tryterra.co`):** unified API across 30+ wearables; per-MAU pricing; HIPAA-eligible BAA.
  - **Vital (`tryvital.io`):** unified wearables + labs (Quest, LabCorp); HIPAA BAA.
  - **Spike API (`spikeapi.com`):** unified wearables; SDK for mobile.
  - **Validic:** enterprise / payer focused; broad device list; high price tier.
  - **Human API (acquired by LexisNexis):** clinical + wearables aggregation; enterprise.
  - **Rook Connect, Heka:** smaller unified-API players.
- **FHIR aggregators:** **1upHealth**, **Particle Health**, **Health Gorilla**, **Redox**, **Datavant** — FHIR / HL7 normalization layers, mostly enterprise.
- **OpenmHealth (`openmhealth.org`):** open data schema for mobile health (Apache 2.0); not a hosting platform — a normalization spec used by some open-source projects.

### 4. Open-source / DIY ecosystem (priority — equal weight to commercial)

#### 4.1 Aggregators / dashboards

- **Home Assistant (`home-assistant.io`):** open-source home automation with health integrations: Withings, Garmin Connect, Fitbit (legacy + Health Connect via companion app), Oura, Eight Sleep (community), Whoop (community), Polar via Bluetooth, Apple HealthKit via the HA companion iOS app, Renpho scales, Mi Fit. Data flows into HA's local SQLite/InfluxDB; visualized via Lovelace / Grafana. Apache 2.0.
- **Gadgetbridge (`gadgetbridge.org`):** Android FOSS app that talks BLE directly to Mi Band, Amazfit, Pebble, Casio GBD, Fossil, Huami, Xiaomi devices — replaces vendor cloud apps. AGPL.
- **HealthKit-Bridge / HealthFit / Health Auto Export / SimpleHealthExport:** iOS apps that surface HealthKit to file/REST/iCloud Drive — varying degrees of open source.
- **Self-hosted health dashboards:** Grafana + InfluxDB + Telegraf is the canonical stack; **Wger** (workout/nutrition self-hosted, AGPL); **Fittrackee** (running tracker, AGPL); **Tactical Run** patterns; **Shimmer Backend** (OpenmHealth reference impl).
- **oh-my-fitness, openHAB health bindings:** smaller projects.
- **OpenScale (F-Droid):** FOSS Android app for many BIA scales (Mi, Renpho, Beurer, Soehnle, Yunmai) via BLE — Rule-6-friendly local-only weight + body comp.
- **Bluetooth GATT Heart Rate Service (UUID `0x180D`):** open standard supported by all chest straps (Polar H10, Wahoo Tickr, Garmin HRM-Pro, Coros) — direct BLE consumption with no vendor cloud.

#### 4.2 CGM / insulin DIY

- **Nightscout (`nightscout.github.io`):** the canonical T1D-community DIY CGM cloud; self-hostable Node.js + MongoDB; REST + websocket API (`/api/v1/entries`, `/sgv`, `/treatments`); ingests from xDrip+, Spike, Loop, AndroidAPS, Tidepool, Dexcom Share, LibreLink uploaders. AGPL. Rule-6-friendly (self-hosted).
- **xDrip+ (Android, GPL):** direct BLE / NFC reads from Libre 2/3, Dexcom G6/G7, Eversense; uploads to Nightscout; local SQLite.
- **Juggluco, Diabox, Glimp:** alt Libre 2/3 readers (Android).
- **Loop / iAPS / Trio (iOS), AndroidAPS, OpenAPS:** DIY closed-loop insulin systems; not directly used by NutriMe but generate the richest CGM + insulin data corpus (relevant context).
- **Tidepool (`tidepool.org`):** non-profit; cloud + open-source uploader for CGM, pump, BG meter data; data donation program; OAuth API; FHIR-compatible exports.
- **OpenAPS data commons:** anonymized donated CGM + insulin time-series for research.

#### 4.3 Standards / self-sovereign

- **OpenmHealth schemas:** JSON schemas for HR, sleep, steps, glucose etc.
- **Solid pods (Tim Berners-Lee's project, `solidproject.org`):** decentralized personal data stores; health data pilot work in NL/UK/Flanders.
- **openEHR (`openehr.org`):** clinical-content modeling standard; archetypes for vitals, labs, etc.; used in NHS England, Norway, Slovenia national programs.
- **Continuity of Care Document (CCDA), HL7 v2, FHIR:** HL7 family standards.
- **NOSH ChartingSystem, OpenEMR, OpenMRS, LibreHealth:** open-source EHRs that store / receive patient data.

#### 4.4 FOSS aggregation libraries

- **`python-garminconnect`** (unofficial, MIT) — scrapes Garmin Connect.
- **`oura-python`, `python-fitbit`, `whoop` (PyPI), `healthkit-to-sqlite` (Simon Willison, MIT)** — pull data into local SQLite.
- **`dexcom` (PyPI)** — Dexcom Share consumer API client.
- **`pylibrelinkup`** — Libre LinkUp client (caregiver path).
- **`apple-health-xml-to-csv`, `qself`** — Apple Health export converters.
- **`fit-tool`, `python-fit-parse`, `fitparse`** — parse Garmin/Wahoo FIT files locally.
- **`gpxpy`, `python-tcxparser`** — GPS/workout files.

### 5. Signal validation literature (peer-reviewed)

> **Tier discipline reminder:** vendor-published validation is Tier 4 unless backed by independent peer-reviewed work. The following are independent peer-reviewed studies (Tier 2/3) of consumer wearable signal accuracy.

- **Apple Watch HR vs. clinical reference (chest strap / ECG):** Wang et al. 2017 (JAMA Cardiology) found Apple Watch HR within ~5 bpm of chest strap during exercise [Tier 3]. Bent et al. 2020 (npj Digital Medicine) found PPG-based wearables (incl. Apple) systematically underperform on darker skin tones during motion [Tier 3].
- **Apple Watch ECG / AFib:** Apple Heart Study (Perez et al. 2019, NEJM) — pragmatic study, ~419k participants; positive predictive value ~84% for irregular pulse notifications followed by ECG [Tier 3, observational]. Subsequent independent studies (Seshadri 2020 *Circulation*, Avram 2021) show single-lead ECG sensitivity for AFib ~85–95%, specificity >95% in stable rhythm cohorts.
- **Whoop sleep staging vs. PSG:** Berryhill et al. 2020 (J Clin Sleep Med); Miller et al. 2020 — mixed accuracy: total sleep time within ~10 min, but stage-level (REM / deep) agreement modest (epoch-by-epoch ~60–70% overall accuracy, common to PPG-based wearables) [Tier 3].
- **Oura Ring sleep + temperature vs. clinical:** de Zambotti et al. 2019 (Behav Sleep Med) for sleep; Maijala et al. 2019 for HR / HRV; Goodale et al. 2024 / 2025 for temperature deviation tracking ovulation. Sleep stage accuracy similar to other PPG wearables (~65–80% epoch agreement); temperature trend reproducible at the day level, less so absolute [Tier 3].
- **Fitbit step count:** Case et al. 2015 (JAMA) — accuracy varies by activity; treadmill walking within ~5%, real-world overestimates. Feehan et al. 2018 (JMIR mHealth) systematic review — Fitbit acceptably accurate for steps in healthy ambulatory adults under controlled walking; less accurate in slow walkers, wheelchair users, free-living [Tier 2 review].
- **Smart-scale BIA vs. DEXA for body composition:** Antonio et al. 2019 (Int J Exerc Sci), McLester et al. 2020 — consumer BIA scales (Withings, Tanita home, Renpho) over- or under-estimate body fat % by 3–8 percentage points vs. DEXA; trend-tracking acceptable, absolute values not [Tier 3]. Kuriyan 2018 review (Indian J Med Res) — BIA limitations well documented.
- **Wearable HRV vs. ECG-derived HRV:** Hinde et al. 2021 (Sensors) systematic review — Polar H10 acceptable as ECG surrogate; wrist PPG (Apple, Garmin, Fitbit, Whoop) acceptable for resting nightly trend, less reliable for short-term / motion / arrhythmic conditions [Tier 2 review]. Nelson & Allen 2019 (PLoS One) — wrist PPG HRV underestimates short RR variability.
- **CGM (consumer + prescription) accuracy:** Dexcom G7 MARD ~8.2% (Garg et al. 2022 *Diabetes Technol Ther*) [Tier 3]. Abbott Libre 2 / 3 MARD ~9–10% (Alva et al. 2022) [Tier 3]. Stelo (consumer Dexcom) clinical performance similar to G7. Wellness CGM (Lingo, Levels) use the same hardware as prescription devices — accuracy ≈ underlying sensor; *interpretation overlay* is the differentiator.
- **Cuffless BP:** Aktiia validation against cuff (Bilo et al. 2021, *Blood Pressure Monitoring*) — within ±5 mmHg under controlled conditions [Tier 3]; performance degrades with arm movement, position changes. Apple Watch / Samsung BP features region-restricted; Samsung BP requires cuff calibration every 4 weeks. ESH 2023 position statement (Stergiou et al.) cautions on cuffless BP for hypertension diagnosis [Tier 1 expert consensus].
- **Skin temperature / ovulation tracking:** Goodale et al. 2024 — Oura ring detected ovulatory shift in 79–89% of cycles, comparable to BBT [Tier 3]. Apple Wrist Temperature similarly performs cycle-tracking at trend level.
- **Skin tone / motion bias in PPG:** Colvonen et al. 2020 (Sleep) editorial; Bent et al. 2020; Koerber et al. 2023 (npj Digital Medicine) — confirmed disparity in green-LED PPG accuracy across Fitzpatrick skin types and during motion.
- **Independent multi-device comparisons:** Stanford / Snyder Lab "wearable head-to-head" series (Shcherbina et al. 2017 *JPM*; Nelson et al. 2020 *npj Digital Medicine*) — energy expenditure poorly estimated across all consumer wearables (>20% error common); HR generally good; sleep highly variable.

### 6. Emerging signals (reference level)

- **Cuffless / continuous BP:**
  - **Aktiia** (CH) — optical PPG bracelet, CE marked, paired cuff; consumer + clinical pilots.
  - **Valencell** — finger / earbud PPG-based BP (IP licensed to OEMs).
  - **Movano Evie Ring** — BP roadmap, not cleared as of training cutoff.
  - **Samsung Galaxy Watch BP** — cuff-calibrated, region-restricted (KR launch 2020, gradual expansion).
  - **Apple BP feature** — rumored / unannounced in shipping units at training cutoff.
- **Non-invasive glucose (research-stage):**
  - **Apple non-invasive glucose project** — long-running internal R&D, Bloomberg-reported, no shipping product.
  - **Quantum Operation, Movano, Know Labs (KnowU), DiaMonTech** — startups making non-invasive claims; *no peer-reviewed validation against capillary / venous reference at clinical accuracy as of training cutoff.* Treat all "non-invasive glucose" consumer claims as Tier 4 / unsupported until peer-reviewed validation publishes.
  - **GWave (Hagar)** — RF-based; early peer-reviewed pilot data.
- **Sweat analysis:**
  - **Epicore Biosystems Nimbl / Connected Hydration** — sweat sodium + rate, NSF + research-grade applications (Gatorade GX patch lineage); peer-reviewed in *Sci Adv* (Bandodkar et al. 2019) [Tier 3].
  - **Nix Hydration Biosensor.**
- **Breath analysis (VOC profiling):**
  - **Owlstone Medical Breath Biopsy** (clinical research instrument).
  - **Lumen** — handheld RER (respiratory exchange ratio) device; peer-reviewed validation mixed (Lorenz et al. 2021 in athletes — moderate agreement with metabolic cart) [Tier 3].
- **Continuous core temperature:**
  - **CORE (greenTEG, CH)** — wearable core-temp (heat-flux + skin temp model); validated in athletic / heat-stress contexts (Verdel et al. 2023, *Sensors*) [Tier 3].
  - **e-Celsius / BodyCap ingestible** — gold-standard core-temp pill, research/medical use.
- **Continuous lactate (research-stage):**
  - **Idro / Numéro Vital** — sweat-lactate prototypes.
  - **Abbott Libre Lactate (announced)** — implantable, clinical roadmap.
  - No consumer-shipping continuous lactate sensor at training cutoff.
- **Other:**
  - **Hydration:** Nix, Epicore (above).
  - **Cortisol patches:** in research (UCLA, Stanford); no consumer product.
  - **Continuous ketones:** Abbott Lingo had ketone variant in early roadmap; Sibio prototype.
  - **Bowel sounds (AbStats):** clinical research only.

### 7. Privacy / data-rights frameworks

> Personal-use product framing means NutriMe does not currently *cross compliance lines at scale*, but the regulatory landscape shapes what a future commercial mode could ingest and from whom — and per Rule 6 the architectural posture treats data with regulated rigor regardless.

- **HIPAA + HITECH (US, 1996 / 2009):** governs PHI held by Covered Entities (providers, payers, clearinghouses) and their Business Associates. Patient-mediated apps that pull data via patient FHIR access (post-Cures Act) generally are *not* Covered Entities; ONC + OCR have explicitly declined to extend HIPAA to patient-controlled apps when the patient directs the disclosure. Caveat: marketing such apps as HIPAA-protected mis-states the regime. **HHS Office for Civil Rights** + **FTC Health Breach Notification Rule** (HBNR, expanded 2024) cover non-HIPAA health apps.
- **21st Century Cures Act §4004 / ONC Cures Act Final Rule (US, 2020):** information-blocking provisions force certified health IT to expose USCDI via FHIR R4 to patient-authorized apps without "special effort." This is the legal mechanism enabling Apple Health Records, Epic SMART-on-FHIR patient apps.
- **GDPR (EU + adopted in UK as UK GDPR + DPA 2018):** Article 9 special-category data covers health; explicit consent required for processing; Article 20 portability right; Article 17 erasure; Data Protection Impact Assessments for high-risk processing; cross-border transfer governed by adequacy + SCCs.
- **EHDS — European Health Data Space (Regulation (EU) 2025/327):** just entered into force at training cutoff; phases in 2025–2028; mandates patient access in standardized FHIR + secondary use framework. Major change to EU patient data flows.
- **PIPEDA (Canada) + provincial PHIPA (Ontario), HIA (Alberta), PHIA (NS/NB/NL/MB), Quebec Law 25:** federal + provincial split; health information held by custodians governed provincially; Quebec Law 25 (in force 2023–2024) tightened consent + cross-border.
- **Privacy Act 1988 + Australian Privacy Principles (APPs) + My Health Records Act 2012 (AU):** APPs apply broadly; specific opt-out PHR regime; cross-border under APP 8.
- **Health Information Privacy Code 2020 (NZ):** health-specific code under the Privacy Act 2020.
- **PIPL (China, 2021) + Data Security Law + Cybersecurity Law:** sensitive personal info (incl. health) requires separate consent + DPIA; strict cross-border export rules (security assessment, standard contract, certification); data localization for "important data" + critical info infra.
- **Act on the Protection of Personal Information (APPI, Japan, 2003 amended 2017/2020/2022):** sensitive-info category includes medical history; PPC oversight; cross-border transfer per equivalent-protection list.
- **PIPA (Korea, 2011) + Bioethics and Safety Act:** sensitive-info regime; my-data initiatives (incl. My HealthWay) have explicit legal underpinnings.
- **LGPD (Brazil, 2018 in force 2020):** GDPR-aligned; sensitive personal data category; ANPD enforcement.
- **Israeli Privacy Protection Law 5741-1981 + Amendment 13 (2024):** sensitive medical info regime; Privacy Protection Authority; aligned increasingly with GDPR via EU adequacy decision.
- **Russian Personal Data Law 152-FZ + Federal Law 242-FZ (data localization, 2015):** processing of Russian citizens' personal data must occur on servers physically in Russia; health data is sensitive. Distribution of foreign health apps to Russia carries additional restrictions post-2022.
- **MDR (EU 2017/745) + IVDR (EU 2017/746):** medical device + in-vitro diagnostic regulation — relevant to wearable feature claims (ECG, AFib, BP, SpO2). Post-Brexit UK runs UKCA / UKMDR (transitional with CE recognition extended).
- **FDA 510(k) / De Novo (US):** clearance path for wearable medical features (Apple ECG, Fitbit ECG, Withings BPM, Dexcom).

### 8. Answers to the open questions in the scope

- **Per-wearable data types / API access / formats / license?** Catalogued in §1; see also §3 aggregators. Common pattern: vendor cloud + OAuth 2.0 + JSON for the modern devices (Whoop, Oura, Withings, Garmin Health, Polar, Coros, Wahoo, Fitbit), HealthKit native framework on Apple, BLE-direct for chest straps and CGM-via-DIY. License floor: free for personal/dev, partner agreement for commercial.
- **Realistic state of doctor-portal patient API access in the US?** Strong: ONC Cures Act §170.315(g)(10) requires certified EHR vendors to expose USCDI via FHIR R4 to patient-authorized apps. Epic, Oracle Health (Cerner), Athena, eCW, Allscripts/Veradigm, NextGen, Greenway, Practice Fusion all certified. Apple Health Records is the most user-friendly entry point. "Request labs through the app" cleanly works only for already-ordered labs flowing back to the patient; *ordering* labs through a third-party app generally still requires DTC partnerships (Quest/LabCorp consumer rails) or telehealth provider integration.
- **OSS / DIY most active ecosystems?** T1D / CGM (Nightscout + xDrip+ + Loop / AAPS) is by far the most mature. Home Assistant has the broadest integration breadth across consumer wearables. Tidepool is the most clinical-credible OSS aggregator. Gadgetbridge owns the BLE-direct-on-Android niche. Standards convergence: FHIR R4 for clinical, OpenmHealth + HL7 IPS for cross-vendor mobile health.
- **Peer-reviewed vs. vendor validation gap?** Vendor validation systematically over-states accuracy vs. independent peer-reviewed work. Key independent finding patterns: (a) HR is generally accurate at rest, degrades with motion + skin tone; (b) sleep-staging consumer wearables ~60–80% epoch agreement vs. PSG, with REM/deep less reliable than total sleep time; (c) BIA scales reliable for trend, unreliable for absolute body composition; (d) energy expenditure broadly poorly estimated (>20% error); (e) consumer ECG single-lead AFib detection genuinely useful at population level but with non-trivial false positives and limited utility for non-AFib arrhythmias.
- **Aggregator with broadest cross-device + cleanest licensing?** For personal-use offline: HealthKit (iOS) + Health Connect (Android) + Home Assistant (cross-platform) covers the field with no commercial license tax. For commercial / multi-tenant: Terra and Vital are the cleanest modern unified APIs; Terra has broader device coverage, Vital has clinical-lab integration.
- **Emerging signals with plausible 1–3 year horizon?** Cuffless BP (Aktiia + OEM-licensed PPG-BP) likely to mainstream as a *trend* signal but not a diagnostic replacement. Continuous core temperature (CORE) for athletes already shipping, athletic adoption growing. OTC CGM (Stelo, Lingo) is the highest-confidence near-term signal — already shipping in 2024–2025, will be commonplace 2026–2027. Sweat sodium (Epicore) niche but real. Non-invasive glucose remains "research stage with consumer-grade marketing"; treat all current consumer claims as Tier 4 until peer-reviewed validation publishes.

### 9. Summary of cross-cutting findings

- **Format convergence:** OAuth 2.0 + JSON is the dominant access modality across modern consumer wearable APIs. FHIR R4 is the dominant clinical access modality. FIT (Garmin/Wahoo), GPX, TCX, CSV, and PDF remain common for activity/lab exports. HL7 v2 still dominates provider-to-provider lab traffic.
- **Local-first feasibility (Rule 6):** strongest with Apple HealthKit, Android Health Connect, Home Assistant + Polar SDK / BLE GATT direct, Gadgetbridge, OpenScale, xDrip+/Nightscout self-hosted. Weakest with Whoop, Oura, Eight Sleep, Garmin Health API (cloud-mediated by design).
- **Doctor-portal access:** US is dramatically ahead due to ONC Cures Act + Apple Health Records adoption; EU EHDS (in force 2025) is the next major wave; AU My Health Record + UK NHS App are mature; Canada fragmented; Asia uneven (Korea + Israel ahead, China heavily walled).
- **Validation gap:** vendor-published validation is consistently more flattering than independent peer-reviewed validation; design and surfacing must use independent peer-reviewed sources (Tier 2/3) when making any signal-quality claim per Rule 7.
- **Highest-leverage data sources for a personal-use holistic-diet system, weighted by signal credibility × accessibility:** (1) Apple HealthKit on-device export incl. ECG + sleep + HRV + workouts; (2) FHIR clinical labs via Apple Health Records / patient FHIR; (3) Withings (BP cuff + scale BIA + Sleep Analyzer) for at-home clinical-grade vitals; (4) CGM (Dexcom Stelo / Abbott Lingo) for episodic glycemic-response inquiry rather than daily input; (5) Garmin / Polar / Coros for training load + GPS context; (6) Nightscout / xDrip+ for any T1D-population user; (7) Oura / Whoop / Fitbit as alternative wrist/ring sources. All others are nice-to-have.

## References

> Convention: full citations follow [citation-style.md](../00-meta/citation-style.md). Accessed-on date 2026-04-28 reflects the date this catalog was assembled; URLs flagged "documentation may have drifted" should be re-verified before the catalog is used for design decisions.

### Vendor / standards documentation (Tier 4 unless backed by independent peer review — usable for "this device measures X" facts only)

- Apple. (2026). *HealthKit | Apple Developer Documentation*. https://developer.apple.com/documentation/healthkit. Accessed 2026-04-28.
- Apple. (2026). *Health Records on iPhone (Apple Health Records)*. https://www.apple.com/healthcare/health-records/. Accessed 2026-04-28.
- Apple. (2026). *Apple Heart Study Overview*. https://www.apple.com/newsroom/2019/03/apple-heart-study-demonstrates-ability-of-wearable-technology-to-detect-atrial-fibrillation/. Accessed 2026-04-28.
- Garmin. (2026). *Garmin Health API Documentation*. https://developer.garmin.com/gc-developer-program/wellness-api/. Accessed 2026-04-28.
- Whoop. (2026). *Whoop Developer API v2*. https://developer.whoop.com/api. Accessed 2026-04-28.
- Oura. (2026). *Oura API v2 Documentation*. https://cloud.ouraring.com/v2/docs. Accessed 2026-04-28.
- Fitbit / Google. (2026). *Fitbit Web API Reference*. https://dev.fitbit.com/build/reference/web-api/. Accessed 2026-04-28.
- Google. (2026). *Health Connect for Android — Developer Guide*. https://developer.android.com/health-and-fitness/guides/health-connect. Accessed 2026-04-28.
- Google. (2024). *Google Fit REST API deprecation notice (sunset 2025-06-30)*. https://developers.google.com/fit/migration. Accessed 2026-04-28.
- Polar. (2026). *Polar AccessLink API*. https://www.polar.com/accesslink-api. Accessed 2026-04-28.
- Polar. (2026). *Polar SDK for iOS / Android (Polar BLE SDK)*. https://github.com/polarofficial/polar-ble-sdk. Accessed 2026-04-28.
- Coros. (2026). *Coros Open API*. https://open.coros.com/. Accessed 2026-04-28.
- Withings. (2026). *Withings Public Cloud API*. https://developer.withings.com/. Accessed 2026-04-28.
- Wahoo. (2026). *Wahoo Cloud API*. https://cloud-api.wahooligan.com/. Accessed 2026-04-28.
- Suunto. (2026). *SuuntoApp Developer*. https://www.suunto.com/Support/suunto-app/. Accessed 2026-04-28.
- Zepp Health (Amazfit). (2026). *Zepp OS Developer Center*. https://docs.zepp.com/. Accessed 2026-04-28.
- Samsung. (2026). *Samsung Health SDK + Health Data Service*. https://developer.samsung.com/health. Accessed 2026-04-28.
- Strava. (2026). *Strava API v3*. https://developers.strava.com/. Accessed 2026-04-28.
- Dexcom. (2026). *Dexcom Developer Portal (G7 / Stelo)*. https://developer.dexcom.com/. Accessed 2026-04-28.
- Abbott. (2026). *LibreView Developer / Provider Portal*. https://www.libreview.com/. Accessed 2026-04-28.
- HL7 International. (2024). *HL7 FHIR R4 — US Core Implementation Guide v6.1*. https://www.hl7.org/fhir/us/core/. Accessed 2026-04-28.
- HL7 International. (2024). *International Patient Summary (IPS) Implementation Guide*. https://www.hl7.org/fhir/uv/ips/. Accessed 2026-04-28.
- ONC. (2020). *21st Century Cures Act: Interoperability, Information Blocking, and the ONC Health IT Certification Program — Final Rule*. https://www.healthit.gov/curesrule/. Accessed 2026-04-28.
- Epic. (2026). *Open.Epic Developer Portal (FHIR R4 USCDI v3)*. https://fhir.epic.com/. Accessed 2026-04-28.
- Oracle Health. (2026). *Oracle Health (formerly Cerner) Developer Portal*. https://docs.oracle.com/en/industries/health/millennium-platform-apis/. Accessed 2026-04-28.
- Athenahealth. (2026). *Athenahealth Developer Portal*. https://docs.athenahealth.com/. Accessed 2026-04-28.
- LabCorp. (2026). *LabCorp Patient APIs / OnDemand*. https://www.labcorp.com/. Accessed 2026-04-28.
- Quest Diagnostics. (2026). *Quanum FHIR / MyQuest API*. https://www.questdiagnostics.com/. Accessed 2026-04-28.
- Nightscout Foundation. (2026). *Nightscout Documentation*. https://nightscout.github.io/. Accessed 2026-04-28.
- xDrip+. (2026). *xDrip+ on GitHub*. https://github.com/NightscoutFoundation/xDrip. Accessed 2026-04-28.
- Tidepool. (2026). *Tidepool Documentation + Open Source*. https://www.tidepool.org/ ; https://github.com/tidepool-org. Accessed 2026-04-28.
- OpenAPS. (2026). *OpenAPS Documentation*. https://openaps.org/. Accessed 2026-04-28.
- Home Assistant. (2026). *Home Assistant Integrations Catalog*. https://www.home-assistant.io/integrations/. Accessed 2026-04-28.
- Gadgetbridge. (2026). *Gadgetbridge*. https://gadgetbridge.org/. Accessed 2026-04-28.
- OpenScale. (2026). *OpenScale on F-Droid*. https://f-droid.org/packages/com.health.openscale/. Accessed 2026-04-28.
- OpenmHealth. (2026). *OpenmHealth Schemas + Shimmer*. https://www.openmhealth.org/. Accessed 2026-04-28.
- openEHR Foundation. (2026). *openEHR Specifications*. https://www.openehr.org/. Accessed 2026-04-28.
- Solid Project. (2026). *Solid (Personal Online Datastores)*. https://solidproject.org/. Accessed 2026-04-28.
- Terra. (2026). *Terra Unified Wearables API*. https://tryterra.co/. Accessed 2026-04-28.
- Vital. (2026). *Vital — Wearables + Lab Testing API*. https://tryvital.io/. Accessed 2026-04-28.
- Spike API. (2026). *Spike API*. https://spikeapi.com/. Accessed 2026-04-28.
- Validic. (2026). *Validic Platform*. https://validic.com/. Accessed 2026-04-28.
- 1upHealth. (2026). *1up FHIR Platform*. https://1up.health/. Accessed 2026-04-28.
- NHS Digital. (2026). *NHS App + GP Connect FHIR*. https://digital.nhs.uk/services/nhs-app and https://digital.nhs.uk/developer/api-catalogue/gp-connect. Accessed 2026-04-28.
- Australian Digital Health Agency. (2026). *My Health Record Developer Resources*. https://developer.digitalhealth.gov.au/. Accessed 2026-04-28.
- Korean MOHW. (2026). *My HealthWay (의료마이데이터)*. https://www.mohw.go.kr/. Accessed 2026-04-28.

### Privacy / data-rights primary sources

- US Department of Health and Human Services. (2013). *HIPAA Privacy Rule (45 CFR Parts 160 and 164)*. https://www.hhs.gov/hipaa/. Accessed 2026-04-28.
- ONC + HHS. (2020). *21st Century Cures Act — Interoperability, Information Blocking, and the ONC Health IT Certification Program; Final Rule*. https://www.federalregister.gov/d/2020-07419. Accessed 2026-04-28.
- US FTC. (2024). *Health Breach Notification Rule (final, 2024)*. https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule. Accessed 2026-04-28.
- European Parliament & Council. (2016). *Regulation (EU) 2016/679 — General Data Protection Regulation*. https://eur-lex.europa.eu/eli/reg/2016/679/oj. Accessed 2026-04-28.
- European Parliament & Council. (2025). *Regulation (EU) 2025/327 — European Health Data Space*. https://eur-lex.europa.eu/eli/reg/2025/327. Accessed 2026-04-28.
- Office of the Privacy Commissioner of Canada. (2018). *PIPEDA*. https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/. Accessed 2026-04-28.
- Office of the Australian Information Commissioner. (2014). *Australian Privacy Principles*. https://www.oaic.gov.au/privacy/australian-privacy-principles. Accessed 2026-04-28.
- New Zealand Privacy Commissioner. (2020). *Health Information Privacy Code 2020*. https://www.privacy.org.nz/. Accessed 2026-04-28.
- Standing Committee of the National People's Congress. (2021). *Personal Information Protection Law (PIPL, China)*. https://www.npc.gov.cn/. Accessed 2026-04-28.
- Personal Information Protection Commission (Japan). (2022). *Act on the Protection of Personal Information (APPI)*. https://www.ppc.go.jp/en/. Accessed 2026-04-28.
- Personal Information Protection Commission (Korea). (2020). *PIPA*. https://www.pipc.go.kr/eng/. Accessed 2026-04-28.
- ANPD (Brazil). (2020). *Lei Geral de Proteção de Dados Pessoais (LGPD, Lei nº 13.709/2018)*. https://www.gov.br/anpd/. Accessed 2026-04-28.
- Israeli Privacy Protection Authority. (2024). *Privacy Protection Law 5741-1981 (incl. Amendment 13)*. https://www.gov.il/en/departments/the_privacy_protection_authority. Accessed 2026-04-28.
- Roskomnadzor (Russia). (2015). *Federal Law 152-FZ on Personal Data + 242-FZ on data localization*. https://rkn.gov.ru/. Accessed 2026-04-28.
- European Parliament & Council. (2017). *Regulation (EU) 2017/745 — Medical Devices Regulation (MDR)*. https://eur-lex.europa.eu/eli/reg/2017/745/oj. Accessed 2026-04-28.

### Peer-reviewed signal-validation literature (Tier 2/3)

- Wang, R., Blackburn, G., Desai, M., Phelan, D., Gillinov, L., Houghtaling, P., & Gillinov, M. (2017). Accuracy of Wrist-Worn Heart Rate Monitors. *JAMA Cardiology*, 2(1), 104–106. https://doi.org/10.1001/jamacardio.2016.3340 [Tier 3].
- Perez, M.V., Mahaffey, K.W., Hedlin, H., et al. (2019). Large-Scale Assessment of a Smartwatch to Identify Atrial Fibrillation (Apple Heart Study). *New England Journal of Medicine*, 381(20), 1909–1917. https://doi.org/10.1056/NEJMoa1901183 [Tier 3].
- Seshadri, D.R., Bittel, B., Browsky, D., Houghtaling, P., Drummond, C.K., Desai, M.Y., & Gillinov, A.M. (2020). Accuracy of Apple Watch for Detection of Atrial Fibrillation. *Circulation*, 141(8), 702–703. https://doi.org/10.1161/CIRCULATIONAHA.119.044126 [Tier 3].
- Bent, B., Goldstein, B.A., Kibbe, W.A., & Dunn, J.P. (2020). Investigating sources of inaccuracy in wearable optical heart rate sensors. *npj Digital Medicine*, 3, 18. https://doi.org/10.1038/s41746-020-0226-6 [Tier 3].
- Koerber, D., Khan, S., Shamsheri, T., Kirubarajan, A., & Mehta, S. (2023). Accuracy of heart rate measurement with wrist-worn wearable devices in various skin tones: a systematic review. *Journal of Racial and Ethnic Health Disparities*, 10, 2676–2684. https://doi.org/10.1007/s40615-022-01446-9 [Tier 2 review].
- Berryhill, S., Morton, C.J., Dean, A., et al. (2020). Effect of wearables on sleep in healthy individuals: a randomized crossover trial and validation study. *Journal of Clinical Sleep Medicine*, 16(5), 775–783. https://doi.org/10.5664/jcsm.8356 [Tier 3].
- Miller, D.J., Lastella, M., Scanlan, A.T., Bellenger, C., Halson, S.L., Roach, G.D., & Sargent, C. (2020). A validation study of the WHOOP strap against polysomnography to assess sleep. *Journal of Sports Sciences*, 38(22), 2631–2636. https://doi.org/10.1080/02640414.2020.1797448 [Tier 3].
- de Zambotti, M., Rosas, L., Colrain, I.M., & Baker, F.C. (2019). The Sleep of the Ring: Comparison of the ŌURA Sleep Tracker Against Polysomnography. *Behavioral Sleep Medicine*, 17(2), 124–136. https://doi.org/10.1080/15402002.2017.1300587 [Tier 3].
- Maijala, A., Kinnunen, H., Koskimäki, H., Jämsä, T., & Kangas, M. (2019). Nocturnal finger skin temperature in menstrual cycle tracking: ambulatory pilot study using a wearable Oura ring. *BMC Women's Health*, 19, 150. https://doi.org/10.1186/s12905-019-0844-9 [Tier 3].
- Goodale, B.M., Shilaih, M., Falco, L., Dammeier, F., Hamvas, G., & Leeners, B. (2024). Wearable Sensors Reveal Menses-Driven Changes in Physiology and Enable Prediction of the Fertile Window: Observational Study. *Journal of Medical Internet Research*, 26, e51844. https://doi.org/10.2196/51844 [Tier 3].
- Case, M.A., Burwick, H.A., Volpp, K.G., & Patel, M.S. (2015). Accuracy of Smartphone Applications and Wearable Devices for Tracking Physical Activity Data. *JAMA*, 313(6), 625–626. https://doi.org/10.1001/jama.2014.17841 [Tier 3].
- Feehan, L.M., Geldman, J., Sayre, E.C., et al. (2018). Accuracy of Fitbit Devices: Systematic Review and Narrative Syntheses of Quantitative Data. *JMIR mHealth and uHealth*, 6(8), e10527. https://doi.org/10.2196/10527 [Tier 2 systematic review].
- Shcherbina, A., Mattsson, C.M., Waggott, D., et al. (2017). Accuracy in Wrist-Worn, Sensor-Based Measurements of Heart Rate and Energy Expenditure in a Diverse Cohort. *Journal of Personalized Medicine*, 7(2), 3. https://doi.org/10.3390/jpm7020003 [Tier 3].
- Nelson, B.W., Allen, N.B. (2019). Accuracy of Consumer Wearable Heart Rate Measurement During an Ecologically Valid 24-Hour Period: Intraindividual Validation Study. *JMIR mHealth uHealth*, 7(3), e10828. https://doi.org/10.2196/10828 [Tier 3].
- Hinde, K., White, G., & Armstrong, N. (2021). Wearable devices suitable for monitoring twenty four hour heart rate variability in military populations. *Sensors*, 21(4), 1061. https://doi.org/10.3390/s21041061 [Tier 2 review].
- Antonio, J., Kenyon, M., Ellerbroek, A., et al. (2019). Comparison of Dual-Energy X-ray Absorptiometry (DXA) Versus a Multi-Frequency Bioelectrical Impedance (InBody 770) Device for Body Composition Assessment after a 4-Week Hypoenergetic Diet. *Journal of Functional Morphology and Kinesiology*, 4(2), 23. https://doi.org/10.3390/jfmk4020023 [Tier 3].
- McLester, C.N., Nickerson, B.S., Kliszczewicz, B.M., & McLester, J.R. (2020). Reliability and Agreement of Various InBody Body Composition Analyzers as Compared to Dual-Energy X-Ray Absorptiometry. *Journal of Clinical Densitometry*, 23(3), 443–450. https://doi.org/10.1016/j.jocd.2018.10.008 [Tier 3].
- Garg, S.K., Kipnes, M., Castorino, K., et al. (2022). Accuracy and Safety of Dexcom G7 Continuous Glucose Monitoring in Adults with Diabetes. *Diabetes Technology & Therapeutics*, 24(6), 373–380. https://doi.org/10.1089/dia.2022.0011 [Tier 3].
- Alva, S., Bailey, T., Brazg, R., Budiman, E.S., Castorino, K., Christiansen, M.P., et al. (2022). Accuracy of a 14-Day Factory-Calibrated Continuous Glucose Monitoring System with Advanced Algorithm in Pediatric and Adult Population with Diabetes. *Journal of Diabetes Science and Technology*, 16(1), 70–77. https://doi.org/10.1177/1932296820958754 [Tier 3].
- Bilo, G., Zorzi, C., Munera, J.E.O., Torlasco, C., Giuli, V., & Parati, G. (2021). Validation of the Aktiia bracelet for cuffless ambulatory blood pressure monitoring. *Blood Pressure Monitoring*, 26(5), 332–339. https://doi.org/10.1097/MBP.0000000000000548 [Tier 3].
- Stergiou, G.S., Mukkamala, R., Avolio, A., et al. (2022). Cuffless blood pressure measuring devices: review and statement by the European Society of Hypertension Working Group on Blood Pressure Monitoring and Cardiovascular Variability. *Journal of Hypertension*, 40(8), 1449–1460. https://doi.org/10.1097/HJH.0000000000003224 [Tier 1 expert consensus].
- Edouard, P., Campo, D., Bartet, P., et al. (2021). Validation of the Withings Sleep Analyzer, an under-the-mattress device for the detection of moderate-severe sleep apnea syndrome. *Journal of Clinical Sleep Medicine*, 17(6), 1217–1227. https://doi.org/10.5664/jcsm.9168 [Tier 3].
- Bandodkar, A.J., Gutruf, P., Choi, J., et al. (2019). Battery-free, skin-interfaced microfluidic/electronic systems for simultaneous electrochemical, colorimetric, and volumetric analysis of sweat. *Science Advances*, 5(1), eaav3294. https://doi.org/10.1126/sciadv.aav3294 [Tier 3].
- Verdel, N., Hadžić, V., Kozinc, Ž., & Šarabon, N. (2023). Validity of the CORE Sensor for Estimating Core Body Temperature During Exercise. *Sensors*, 23(20), 8403. https://doi.org/10.3390/s23208403 [Tier 3].
- Lorenz, K.A., Yeshurun, S., Aziz, R., et al. (2021). A Handheld Metabolic Device (Lumen) to Measure Fuel Utilization in Healthy Young Adults: Device Validation Study. *Interactive Journal of Medical Research*, 10(2), e25371. https://doi.org/10.2196/25371 [Tier 3].

### Note on sources.md

Per the brief, this sweep does not edit `00-meta/sources.md`. URLs above should be merged into the master `sources.md` in a consolidation pass; many will overlap with sister sweeps (FHIR US Core in particular intersects sweep #3 / #5 / #10).
