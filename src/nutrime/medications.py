"""Drug–nutrient interaction rails — sweep #10 §6, built per issue #46.

Members disclose medications at intake (free text, like conditions); this
registry deterministically maps each disclosure to food-relevant rails:

- ``avoid_terms`` — recipe-ingredient exclusions (recall-biased matching
  downstream, same as allergens/life-stage rails). Only interactions
  where the labeled guidance is *avoid the food* become exclusions.
- ``plan_note`` — a planner-prompt rail. Phrased mechanism-level, never
  naming the drug: PhiCategory.MEDICATIONS is NOT in the planner's
  envelope, so medication names must never ride household_note into a
  crossing — only the food consequence does.
- ``note`` — user-facing explanation, including timing guidance that a
  meal planner can't enforce (take-with/-without-food windows live with
  the prescriber; we surface them once, at the profile, per the
  alert-fatigue findings in scope.md §6.4).

Like the condition registry this is **hardcoded and outside any LLM** —
rails are computed from the profile at every use, never stored, so a
registry correction applies to already-disclosed medications.

Sources: scope.md §6.2 base table as corrected by the 2026-10 source
check on issue #46 (all 38 rows checked against FDA labels via DailyMed,
MedlinePlus, NHS, NIH ODS, and Bailey 2013 CMAJ
https://doi.org/10.1503/cmaj.120951). The corrections applied here:

- Statin + grapefruit is plain avoidance — the "dose-timing per
  prescriber" alternative is dropped (Bailey 2013: juice 24 h earlier
  still gives ~25% of maximum effect; simvastatin label says avoid).
- Erythromycin/clarithromycin + grapefruit is HIGH risk (torsade de
  pointes per Bailey 2013), not "minimal".
- Metronidazole/tinidazole/disulfiram/acitretin + alcohol added
  (missing from the base table); disulfiram includes hidden alcohol
  in "sauces, vinegars" per its label.
- Licorice is keyed to digoxin and potassium-LOSING diuretics, not
  spironolactone (which licorice counters, per Merck).
- MAOI tyramine gating is tiered: hard exclusion for the classic
  irreversible MAOIs, awareness-only for linezolid ("large amounts")
  and the 6 mg selegiline patch (no diet change per label).
- Methotrexate + folate is split by indication (supplement guidance
  belongs to the prescriber; we only carry the note).
- Potassium: ACE-i/ARB/K-sparing rails cover supplements as well as
  salt substitutes (spironolactone/lisinopril/losartan labels).
- Aspirin + vitamin C/folate row dropped entirely (unsourceable).
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass

# Rail kinds, tiered per scope.md §6.4 (alert-fatigue): exclusions are
# enforced silently in search/planner; consistency and awareness rails
# are information, surfaced once at the profile.
EXCLUSION = "exclusion"
CONSISTENCY = "consistency"
AWARENESS = "awareness"

# Grapefruit-family CYP3A4 terms (Bailey 2013: also Seville/sour orange
# and pomelo; regular sweet orange juice is fine).
_GRAPEFRUIT: tuple[str, ...] = (
    "grapefruit", "pomelo", "seville orange", "sour orange",
)

# Tyramine pressor-crisis list for irreversible MAOIs — recall-biased:
# aged cheeses broadly, cured/fermented meats, fermented soy, aged/kept
# drinks. A missed match is a hypertensive crisis, so err wide.
_TYRAMINE: tuple[str, ...] = (
    "aged cheese", "blue cheese", "gorgonzola", "stilton", "roquefort",
    "cheddar", "parmesan", "gouda", "gruyere", "provolone",
    "swiss cheese", "camembert", "brie",
    "salami", "pepperoni", "chorizo", "prosciutto", "cured meat",
    "dry sausage", "summer sausage", "mortadella",
    "soy sauce", "miso", "fish sauce", "sauerkraut", "kimchi",
    "fava bean", "broad bean", "marmite", "vegemite",
    "beer", "wine",
)

# Alcohol as a recipe ingredient — mirrors the life-stage pregnancy
# list so the two rails exclude the same things.
_ALCOHOL: tuple[str, ...] = (
    "alcohol", "wine", "beer", "rum", "brandy", "bourbon", "whiskey",
    "vodka", "sake", "mirin", "sherry", "cooking wine", "liqueur",
)

# Disulfiram's label extends to alcohol hidden in "sauces, vinegars" —
# the only rail that reaches vinegar.
_ALCOHOL_HIDDEN: tuple[str, ...] = _ALCOHOL + (
    "vinegar", "vanilla extract",
)

_SALT_SUBSTITUTE: tuple[str, ...] = (
    "salt substitute", "potassium chloride", "lite salt", "lo-salt",
    "no-salt",
)


@dataclass(frozen=True)
class MedicationInfo:
    canonical: str
    kind: str                         # exclusion | consistency | awareness
    avoid_terms: tuple[str, ...] = ()
    plan_note: str = ""               # mechanism-level; NEVER names the drug
    note: str = ""                    # user-facing explanation + timing


def _m(canonical, kind, avoid_terms=(), plan_note="", note=""):
    return MedicationInfo(canonical, kind, tuple(avoid_terms), plan_note, note)


# Registry per scope.md §6.2 as corrected on #46. Patterns are matched
# case-insensitively against the member's free-text disclosure; first
# match wins, so more specific patterns (selegiline patch, pravastatin)
# sit above the general ones (MAOI, statin).
_REGISTRY: tuple[tuple[re.Pattern[str], MedicationInfo], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), info)
    for pattern, info in (
        # -- anticoagulation ------------------------------------------------
        (r"\b(warfarin|coumadin|jantoven)",
         _m("warfarin", CONSISTENCY,
            avoid_terms=("natto",),
            plan_note="an eater needs day-to-day CONSISTENT vitamin K — "
                      "keep leafy greens steady across the week (neither "
                      "load-up days nor none), and no natto",
            note="Warfarin works against vitamin K: the goal is a steady "
                 "amount of leafy greens week to week, not avoiding them. "
                 "Natto is effectively contraindicated. Keep alcohol "
                 "moderate and steady, avoid St John's Wort, and clear any "
                 "herbal supplement with the prescriber (INR monitoring "
                 "catches drift).")),
        # -- MAOIs: tiered per the #46 correction ---------------------------
        (r"\bselegiline\b.{0,20}\b(patch|transdermal)|\bemsam\b",
         _m("selegiline patch", AWARENESS,
            note="At the 6 mg/24 h patch dose the label requires no "
                 "dietary change. Higher patch doses carry the tyramine "
                 "restrictions — confirm the dose with the prescriber.")),
        (r"\blinezolid\b|\bzyvox\b",
         _m("linezolid", AWARENESS,
            plan_note="an eater should not get tyramine-heavy meals — go "
                      "easy on aged cheeses and cured or fermented foods",
            note="Linezolid is a weak MAO inhibitor: the label says avoid "
                 "LARGE amounts of tyramine-rich food (aged cheese, cured "
                 "meats, fermented products) — moderation, not the full "
                 "MAOI exclusion diet.")),
        (r"\b(phenelzine|nardil|tranylcypromine|parnate|isocarboxazid|"
         r"marplan|selegiline|methylene\s+blue|\bmaoi?\b|monoamine\s+"
         r"oxidase)",
         _m("MAO inhibitor", EXCLUSION,
            avoid_terms=_TYRAMINE,
            plan_note="an eater must strictly avoid tyramine — no aged "
                      "cheeses, cured or fermented meats, soy sauce, miso, "
                      "sauerkraut, kimchi, fava or broad beans, or "
                      "beer/wine in any dish",
            note="MAO inhibitors block the enzyme that clears tyramine; "
                 "aged, cured and fermented foods can trigger a dangerous "
                 "blood-pressure crisis. The strict avoidance list is "
                 "enforced in search and plans. (Taking phenelzine: also "
                 "keep caffeine modest.)")),
        # -- statins: specific low-interaction ones above the class ---------
        (r"\b(pravastatin|pravachol|rosuvastatin|crestor|fluvastatin|"
         r"pitavastatin)",
         _m("statin (minimal grapefruit interaction)", AWARENESS,
            note="This statin is minimally affected by grapefruit "
                 "(it isn't cleared by the CYP3A4 pathway grapefruit "
                 "blocks); no food exclusion needed.")),
        (r"\b(simvastatin|zocor|lovastatin|mevacor|altoprev|atorvastatin|"
         r"lipitor|statin)\b",
         _m("statin", EXCLUSION,
            avoid_terms=_GRAPEFRUIT,
            plan_note="an eater must avoid grapefruit, pomelo and Seville "
                      "orange entirely",
            note="Grapefruit blocks the enzyme that clears this statin, "
                 "raising muscle-damage risk. The effect lasts a day or "
                 "more after one serving, so timing doses around "
                 "grapefruit does NOT make it safe — the label says "
                 "avoid. Pravastatin and rosuvastatin are alternatives "
                 "that don't interact (a prescriber conversation).")),
        # -- the grapefruit/CYP3A4 immunosuppressant + oncologic class ------
        (r"\b(tacrolimus|prograf|envarsus|astagraf|cyclosporine|neoral|"
         r"sandimmune|sirolimus|rapamune|everolimus|afinitor|zortress|"
         r"lomitapide|juxtapid|nilotinib|tasigna|dasatinib|sprycel|"
         r"ibrutinib|imbruvica|palbociclib|ibrance|venetoclax|venclexta|"
         r"lapatinib|tykerb)",
         _m("CYP3A4-sensitive medication", EXCLUSION,
            avoid_terms=_GRAPEFRUIT + ("pomegranate",),
            plan_note="an eater must avoid grapefruit, pomelo, Seville "
                      "orange and pomegranate entirely",
            note="Grapefruit (and for some of these, pomegranate) blocks "
                 "the enzyme that clears this medication, pushing levels "
                 "into the toxic range. Avoid St John's Wort too (it has "
                 "the opposite effect). Extended-release tacrolimus: "
                 "don't take with alcohol — it speeds the release.")),
        (r"\b(erythromycin|clarithromycin|biaxin)",
         _m("macrolide antibiotic (erythromycin/clarithromycin)",
            EXCLUSION,
            avoid_terms=_GRAPEFRUIT,
            plan_note="an eater must avoid grapefruit, pomelo and Seville "
                      "orange while on a current antibiotic course",
            note="Grapefruit raises erythromycin/clarithromycin levels — "
                 "a heart-rhythm (torsade de pointes) risk, rated high "
                 "severity. Skip grapefruit for the course.")),
        # -- alcohol hard-stops ----------------------------------------------
        (r"\b(metronidazole|flagyl)",
         _m("metronidazole", EXCLUSION,
            avoid_terms=_ALCOHOL,
            plan_note="an eater must have no alcohol in any form, "
                      "including in cooking",
            note="Alcohol with metronidazole causes flushing, vomiting "
                 "and racing heart (a disulfiram-like reaction). The "
                 "label: no alcohol or propylene-glycol products during "
                 "treatment and for at least 3 days after the last "
                 "dose — including alcohol cooked into dishes.")),
        (r"\b(tinidazole|tindamax)",
         _m("tinidazole", EXCLUSION,
            avoid_terms=_ALCOHOL,
            plan_note="an eater must have no alcohol in any form, "
                      "including in cooking",
            note="Same reaction as metronidazole: no alcohol during "
                 "treatment and for 3 days after.")),
        (r"\b(disulfiram|antabuse)",
         _m("disulfiram", EXCLUSION,
            avoid_terms=_ALCOHOL_HIDDEN,
            plan_note="an eater must have absolutely no alcohol, "
                      "including hidden alcohol in sauces, vinegars and "
                      "extracts",
            note="Disulfiram reacts with ANY alcohol — the label calls "
                 "out sauces, vinegars and cough mixtures — and the "
                 "reaction can occur up to 14 days after a dose. "
                 "Vinegar and extracts are excluded from recipes too.")),
        (r"\b(acitretin|soriatane)",
         _m("acitretin", EXCLUSION,
            avoid_terms=_ALCOHOL,
            plan_note="an eater must have no alcohol in any form, "
                      "including in cooking",
            note="Alcohol converts acitretin into a form that stays in "
                 "the body for years; the label says people who can "
                 "become pregnant must not ingest any ethanol during "
                 "treatment and for 2 months after. Also avoid vitamin A "
                 "supplements (additive toxicity).")),
        (r"\b(isotretinoin|accutane|absorica)",
         _m("isotretinoin", AWARENESS,
            note="Avoid vitamin A supplements (additive toxicity) and "
                 "keep alcohol light. Take with food per label.")),
        # -- potassium axis ---------------------------------------------------
        (r"\b(spironolactone|aldactone|eplerenone|inspra|amiloride|"
         r"triamterene|dyrenium)",
         _m("potassium-sparing diuretic", EXCLUSION,
            avoid_terms=_SALT_SUBSTITUTE,
            plan_note="an eater must avoid potassium-chloride salt "
                      "substitutes; keep very potassium-heavy meals "
                      "occasional rather than daily",
            note="This medication keeps potassium in the body. Salt "
                 "substitutes are potassium chloride and are excluded; "
                 "potassium supplements can cause severe hyperkalemia "
                 "(label warning) — only with prescriber sign-off. "
                 "High-potassium foods are fine in normal amounts; the "
                 "prescriber monitors levels.")),
        (r"\b(lisinopril|prinivil|zestril|enalapril|vasotec|ramipril|"
         r"altace|benazepril|lotensin|captopril|quinapril|perindopril|"
         r"ace\s+inhibitor|losartan|cozaar|valsartan|diovan|irbesartan|"
         r"avapro|olmesartan|benicar|candesartan|atacand|telmisartan|"
         r"micardis|\barbs?\b)",
         _m("ACE inhibitor / ARB", EXCLUSION,
            avoid_terms=_SALT_SUBSTITUTE,
            plan_note="an eater must avoid potassium-chloride salt "
                      "substitutes",
            note="Blood-pressure medicines in this family raise "
                 "potassium. Salt substitutes (potassium chloride) are "
                 "excluded; potassium supplements need prescriber "
                 "sign-off (labels warn of severe hyperkalemia). "
                 "Potassium-rich foods in normal amounts are fine.")),
        # -- licorice: digoxin + potassium-LOSING diuretics (#46 fix) --------
        (r"\b(digoxin|lanoxin)",
         _m("digoxin", EXCLUSION,
            avoid_terms=("licorice", "liquorice"),
            plan_note="an eater must avoid licorice",
            note="Licorice (real licorice root, including in teas and "
                 "candies) depletes potassium, which makes digoxin "
                 "toxicity more likely. Keep fiber-heavy supplements "
                 "apart from the dose.")),
        (r"\b(furosemide|lasix|bumetanide|bumex|torsemide|"
         r"hydrochlorothiazide|hctz|chlorthalidone|indapamide|"
         r"loop\s+diuretic|thiazide)",
         _m("potassium-losing diuretic", EXCLUSION,
            avoid_terms=("licorice", "liquorice"),
            plan_note="an eater must avoid licorice; favor meals with "
                      "potassium- and magnesium-rich vegetables",
            note="Loop and thiazide diuretics flush potassium and "
                 "magnesium; licorice makes that worse (Merck: avoid). "
                 "Thiazides also retain calcium — clear vitamin D or "
                 "calcium supplements with the prescriber.")),
        # -- consistency rails -------------------------------------------------
        (r"\b(lithium|lithobid|eskalith)",
         _m("lithium", CONSISTENCY,
            plan_note="an eater needs CONSISTENT day-to-day sodium and "
                      "fluid — no crash low-salt days and no salt-load "
                      "days; keep caffeine steady",
            note="The kidneys handle lithium like sodium: a sudden "
                 "low-salt diet raises lithium levels, a salt binge "
                 "drops them. Keep salt, fluids and caffeine steady "
                 "rather than low.")),
        (r"\b(carbidopa|levodopa|sinemet|rytary|duopa)",
         _m("carbidopa/levodopa", CONSISTENCY,
            plan_note="an eater absorbs their medication poorly with "
                      "high-protein meals — keep protein portions "
                      "moderate and consistent, with the day's protein "
                      "weighted toward the evening meal",
            note="Dietary protein competes with levodopa for absorption. "
                 "Distributing protein away from doses (often toward "
                 "evening) helps — coordinate the pattern with "
                 "neurology.")),
        (r"\b(insulin|sulfonylurea|glipizide|glucotrol|glyburide|"
         r"glimepiride|amaryl)",
         _m("insulin / sulfonylurea", CONSISTENCY,
            plan_note="an eater doses against carbohydrate — favor meals "
                      "with clear, steady carbohydrate content; alcohol "
                      "only alongside food",
            note="Hypoglycemia risk: meals with predictable carbohydrate "
                 "make dosing safer, and alcohol on an empty stomach can "
                 "drop blood sugar hours later. Carb targets belong to "
                 "the care team.")),
        (r"\b(semaglutide|ozempic|wegovy|rybelsus|tirzepatide|mounjaro|"
         r"zepbound|dulaglutide|trulicity|liraglutide|victoza|saxenda|"
         r"glp.?1)",
         _m("GLP-1 receptor agonist", CONSISTENCY,
            plan_note="an eater tolerates smaller, lower-fat meals best — "
                      "favor modest portions and go easy on very rich or "
                      "fried dishes",
            note="These medicines slow stomach emptying; large or very "
                 "fatty meals commonly cause nausea (a comfort guideline, "
                 "not a label rule). Taking the oral form (Rybelsus): "
                 "empty stomach, plain water (≤ 4 oz), then wait 30 "
                 "minutes before eating — that one is the label.")),
        # -- awareness / timing rails ------------------------------------------
        (r"\b(levothyroxine|synthroid|levoxyl|tirosint|unithroid)",
         _m("levothyroxine", AWARENESS,
            note="Take 30–60 minutes before breakfast with water; keep "
                 "calcium, iron, soy and coffee at least 4 hours from "
                 "the dose (they block absorption). On a PPI "
                 "(omeprazole etc.) spacing doesn't help — acid stays "
                 "suppressed — so the label says monitor TSH instead.")),
        (r"\b(alendronate|fosamax|ibandronate|boniva|risedronate\b.{0,20}"
         r"\b(delayed|atelvia)|atelvia|risedronate|actonel|"
         r"bisphosphonate)",
         _m("oral bisphosphonate", AWARENESS,
            note="Take on an empty stomach with plain water only, then "
                 "stay upright and skip all food, coffee, juice and "
                 "calcium for 30–60 minutes (per the specific drug's "
                 "label). The exception: delayed-release risedronate "
                 "(Atelvia) is taken right AFTER breakfast.")),
        (r"\b(doxycycline|minocycline|tetracycline)",
         _m("tetracycline antibiotic", AWARENESS,
            note="Dairy, calcium, iron, magnesium and antacids bind this "
                 "antibiotic. Spacing differs by drug — tetracycline "
                 "itself also needs an empty stomach — follow the "
                 "pharmacy label for the specific one.")),
        (r"\b(ciprofloxacin|cipro\b|levofloxacin|levaquin|moxifloxacin|"
         r"avelox|fluoroquinolone)",
         _m("fluoroquinolone antibiotic", AWARENESS,
            note="Dairy and mineral supplements bind this antibiotic; "
                 "the separation window differs by drug (moxifloxacin: "
                 "4 h before or 8 h after) — follow the pharmacy label. "
                 "Ciprofloxacin also slows caffeine clearance.")),
        (r"\b(raltegravir|isentress)",
         _m("raltegravir", AWARENESS,
            note="Don't take with aluminum or magnesium antacids at all "
                 "— separating doses in time isn't enough (label). "
                 "Calcium-carbonate antacids are OK with the daily "
                 "formulation.")),
        (r"\b(dolutegravir|tivicay|bictegravir|biktarvy)",
         _m("integrase inhibitor", AWARENESS,
            note="Calcium, iron, magnesium, aluminum and zinc "
                 "(supplements, antacids) bind this medication — take "
                 "it 2 h before or 6 h after them, or together WITH "
                 "food for the Ca/Fe case, per label.")),
        (r"\b(rilpivirine|edurant|complera|odefsey)",
         _m("rilpivirine", AWARENESS,
            note="Take with a meal (a protein drink doesn't count) — "
                 "absorption depends on it.")),
        (r"\b(efavirenz|sustiva|atripla)",
         _m("efavirenz", AWARENESS,
            note="Take on an empty stomach, preferably at bedtime — "
                 "high-fat meals increase absorption and CNS side "
                 "effects.")),
        (r"\b(metformin|glucophage|glumetza)",
         _m("metformin", AWARENESS,
            note="Long-term use lowers B12 absorption — periodic B12 "
                 "checks per prescriber, and B12-rich foods help. Heavy "
                 "or binge drinking raises lactic-acidosis risk "
                 "(label) — keep alcohol light.")),
        (r"\b(omeprazole|prilosec|esomeprazole|nexium|lansoprazole|"
         r"prevacid|pantoprazole|protonix|rabeprazole|\bppi\b|proton.?"
         r"pump)",
         _m("proton-pump inhibitor (long-term)", AWARENESS,
            note="Long-term acid suppression lowers B12, magnesium and "
                 "non-heme iron absorption; calcium citrate absorbs "
                 "better than carbonate in that setting. Worth raising "
                 "at a check-up if use is ongoing.")),
        (r"\b(phenytoin|dilantin|phenytek)",
         _m("phenytoin", AWARENESS,
            note="Folic-acid supplements can lower phenytoin levels "
                 "(label) — don't start one without the prescriber. "
                 "Chronic use depletes folate and vitamin D; food-first "
                 "sources are safe.")),
        (r"\b(methotrexate|trexall|otrexup|rasuvo)",
         _m("methotrexate", AWARENESS,
            note="Folic-acid supplementation is standard alongside "
                 "methotrexate for rheumatoid arthritis and psoriasis — "
                 "but for cancer treatment folic acid can blunt the "
                 "drug, so supplement use follows the indication: "
                 "prescriber's call, not a default. Keep alcohol light "
                 "(liver risk).")),
        (r"\b(isoniazid|\binh\b|rifampin.{0,15}isoniazid|rifamate)",
         _m("isoniazid", AWARENESS,
            plan_note="an eater should not get tyramine- or "
                      "histamine-heavy meals — go easy on aged cheeses "
                      "and cured or fermented fish",
            note="Isoniazid weakly blocks tyramine and histamine "
                 "clearance (flushing/headache reactions with aged "
                 "cheese and cured fish) and depletes vitamin B6 — B6 "
                 "supplementation is usually co-prescribed.")),
        (r"\b(theophylline|theo.?dur|uniphyl)",
         _m("theophylline", AWARENESS,
            note="Caffeine stacks with it (same drug family) and "
                 "charbroiled food or sudden high-protein/low-carb "
                 "shifts change its clearance — a narrow-margin drug, "
                 "so keep those steady.")),
        (r"\b(orlistat|xenical|alli)",
         _m("orlistat", AWARENESS,
            note="Blocks fat absorption, including vitamins A, D, E and "
                 "K — take a multivitamin at bedtime, well apart from "
                 "doses.")),
        (r"\b(cholestyramine|questran|colestipol|colesevelam|welchol|"
         r"bile.?acid\s+sequestrant)",
         _m("bile-acid sequestrant", AWARENESS,
            note="Binds fat-soluble vitamins (A, D, E, K) and folate — "
                 "take other medicines and vitamins 1 h before or 4–6 h "
                 "after it.")),
        (r"\b(apixaban|eliquis|rivaroxaban|xarelto|edoxaban|savaysa|"
         r"dabigatran|pradaxa|\bdoac\b)",
         _m("direct oral anticoagulant", AWARENESS,
            note="Much less food-dependent than warfarin — no vitamin-K "
                 "balancing. Avoid St John's Wort (reduces the drug's "
                 "effect); rivaroxaban at 15/20 mg is taken WITH food.")),
        (r"\b(ssri|snri|sertraline|zoloft|fluoxetine|prozac|escitalopram|"
         r"lexapro|citalopram|celexa|paroxetine|paxil|venlafaxine|"
         r"effexor|duloxetine|cymbalta|tramadol|sumatriptan|triptan)",
         _m("serotonergic medication", AWARENESS,
            note="Avoid St John's Wort (serotonin-syndrome risk). No "
                 "food restrictions.")),
    )
)

# Chips offered in the intake UI — common disclosures, phrased the way
# the matcher recognizes them. Free text is always accepted alongside.
COMMON_MEDICATIONS: tuple[str, ...] = (
    "warfarin",
    "a statin",
    "levothyroxine",
    "metformin",
    "insulin",
    "an ACE inhibitor or ARB",
    "a GLP-1 (Ozempic, Mounjaro…)",
    "an MAOI antidepressant",
    "lithium",
    "a diuretic (water pill)",
)


def classify(disclosure_text: str) -> MedicationInfo | None:
    """Deterministically classify one free-text medication disclosure.

    Unlike conditions, an unrecognized medication yields ``None`` rather
    than a fail-closed gate: most medications have no food interaction,
    and gating every unknown drug would bury the real rails in noise
    (scope.md §6.4 alert fatigue). The dynamic-research-expansion
    pipeline (#46, still open) is the planned path for unknown drugs;
    until then the profile page says unrecognized entries carry no rails.
    """
    text = disclosure_text.strip()
    if not text:
        return None
    for pattern, info in _REGISTRY:
        if pattern.search(text):
            return info
    return None


@dataclass(frozen=True)
class MedicationRails:
    """The household's aggregate drug–nutrient rails."""

    avoid_terms: frozenset[str]
    plan_notes: tuple[str, ...]            # injected into every crossing
    medications: tuple[MedicationInfo, ...]
    unrecognized: tuple[str, ...]          # disclosures with no registry hit


def medication_rails(disclosures: list[str] | tuple[str, ...]) -> MedicationRails:
    """Rails for a list of free-text disclosures (deduplicated by canonical)."""
    avoid: set[str] = set()
    notes: list[str] = []
    infos: list[MedicationInfo] = []
    unknown: list[str] = []
    seen: set[str] = set()
    for raw in disclosures:
        info = classify(raw)
        if info is None:
            if raw.strip():
                unknown.append(raw.strip())
            continue
        if info.canonical in seen:
            continue
        seen.add(info.canonical)
        infos.append(info)
        avoid.update(info.avoid_terms)
        if info.plan_note:
            notes.append(info.plan_note)
    return MedicationRails(
        avoid_terms=frozenset(avoid),
        plan_notes=tuple(notes),
        medications=tuple(infos),
        unrecognized=tuple(unknown),
    )


def household_medication_rails(
    conn: sqlite3.Connection, tenant_id: str
) -> MedicationRails:
    """Rails for every ACTIVE member's disclosed medications."""
    from nutrime.intake.store import household_profiles

    disclosures: list[str] = []
    for profile in household_profiles(conn, tenant_id).values():
        disclosures.extend(profile.medications)
    return medication_rails(disclosures)
