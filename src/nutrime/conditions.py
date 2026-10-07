"""Clinical condition gating — sweep #10's refuse / gate / disclaimer framework.

Planned in research/10-clinical-condition-gating/scope.md (2026-04-28) and
unbuilt until now: members disclose conditions at intake; this registry
deterministically maps each disclosure to a behavior:

- ``refuse`` — the system declines to generate meal plans while the
  condition is in the household ("unauthorized intervention is harmful":
  active eating disorders, early post-bariatric, oncology nutrition during
  active treatment, severe CKD, T1D without endocrinologist coordination).
- ``gate`` — plans proceed with strict rails: the condition's constraint
  line is injected into every planner crossing and surfaced to the user.
- ``disclaimer`` — plans proceed; Rule 1 consult-professional handling
  (surface_rules.household_sensitivities picks the disclosure up as an
  eater sensitivity) plus a soft planner nudge where one exists.

Like the constitutional rule layer, this is **hardcoded and outside any
LLM** — behavior is computed from the registry at every use, never stored,
so a registry correction applies to already-disclosed conditions.

Refer-out specialties follow the scope doc's mapping; surfaced as
awareness ("who to look for"), never as provider integration.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass

REFUSE = "refuse"
GATE = "gate"
DISCLAIMER = "disclaimer"

_RDN = "a registered dietitian nutritionist (RDN)"


@dataclass(frozen=True)
class ConditionInfo:
    canonical: str
    behavior: str            # refuse | gate | disclaimer
    specialties: tuple[str, ...]
    plan_note: str = ""      # constraint line for the planner prompt ("" = none)
    note: str = ""           # one-line user-facing behavior explanation


def _c(canonical, behavior, specialties, plan_note="", note=""):
    return ConditionInfo(canonical, behavior, tuple(specialties), plan_note, note)


# "This is about a child" marker for the pediatric rows — the
# disclosure usually says so ("my son's...", "pediatric...", "child
# with..."). Rows that are pediatric-only by nature (FPIES, EoE,
# biliary atresia…) match without it.
_PED = (
    r"\b(pediatric|paediatric|child(?:hood)?(?:.?s)?|kid(?:.?s)?|"
    r"son(?:.?s)?|daughter(?:.?s)?|toddler(?:.?s)?|infant|baby|"
    r"adolescent|teen(?:ager)?(?:.?s)?)\b"
)

# Registry per scope.md "Conditions in scope (initial)". Patterns are
# matched case-insensitively against the member's free-text disclosure.
# Order matters: the first match wins, so the more specific pattern
# (e.g. T1D *with* coordination) sits above the general one.
_REGISTRY: tuple[tuple[re.Pattern[str], ConditionInfo], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), info)
    for pattern, info in (
        # -- refuse ----------------------------------------------------------
        # \b removed before bulimi/anorexi stems is deliberate where a
        # compound hides the stem: "diabulimia" (#58) has no word boundary
        # before "bulimi".
        (r"anorexi|bulimi|\b(binge.?eating|arfid|osfed|t1de|"
         r"eating\s+disorder)",
         _c("active eating disorder", REFUSE,
            ("an eating-disorder treatment team (psychiatry + RDN)",),
            note="Meal planning during active eating-disorder recovery belongs "
                 "with the treatment team, not an app.")),
        # Bariatric: maintenance-phase wording gates; anything else —
        # including bare procedure names (#58: "gastric bypass", "sleeve
        # gastrectomy" fell through to disclaimer) — refuses, since the
        # early staged phase is the dangerous one and the disclosure
        # doesn't say which phase the eater is in.
        (r"\b(bariatric|gastric\s+bypass|sleeve\s+gastrectomy|gastric\s+"
         r"sleeve|gastric\s+band|lap.?band|rygb|roux.?en.?y|vsg|oagb|"
         r"duodenal\s+switch)\b.{0,40}\b(maintenance|stable|years?\s+ago)|"
         r"\b(maintenance|stable|years?\s+ago)\b.{0,40}\b(bariatric|gastric\s+"
         r"bypass|sleeve\s+gastrectomy|gastric\s+sleeve|rygb|vsg|oagb)",
         _c("post-bariatric (maintenance)", GATE,
            ("the bariatric surgery team", "a bariatric RDN"),
            plan_note="an eater is in post-bariatric maintenance — favor "
                      "protein-forward, smaller-portion meals; avoid "
                      "carbonated drinks and slider foods",
            note="Maintenance-phase post-bariatric: plans proceed with "
                 "protein-first, portion-aware rails.")),
        (r"\b(bariatric|gastric\s+bypass|sleeve\s+gastrectomy|gastric\s+"
         r"sleeve|gastric\s+band|lap.?band|rygb|roux.?en.?y|vsg\b|oagb|"
         r"duodenal\s+switch)",
         _c("post-bariatric (phase unknown or early)", REFUSE,
            ("the bariatric surgery team", "a bariatric RDN"),
            note="Early post-bariatric nutrition is staged and medically "
                 "supervised; NutriMe stands back until maintenance. If "
                 "you're 6+ months out and stable, say so in the "
                 "disclosure (e.g. \"gastric bypass, stable maintenance\") "
                 "and NutriMe proceeds with protein-first rails.")),
        (r"\b(active|current|undergoing).{0,25}(cancer|chemo|radiation|oncolog)|"
         r"\b(chemo(therapy)?|radiation\s+therapy)\b",
         _c("oncology nutrition (active treatment)", REFUSE,
            ("the oncology team", "an oncology RDN"),
            note="Nutrition during active cancer treatment is managed by the "
                 "oncology team.")),
        # Stage accepts Roman numerals (#58: "stage IV" parsed as early).
        (r"\b(ckd|kidney\s+disease).{0,15}(stage\s*(4|5|iv\b|v\b)|severe)|"
         r"\bstage\s*(4|5|iv\b|v\b).{0,15}(ckd|kidney)|"
         r"\b(dialysis|kidney\s+failure|esrd|renal\s+failure)\b",
         _c("severe chronic kidney disease", REFUSE,
            ("a nephrologist", "a renal RDN"),
            note="Potassium, phosphorus, protein and fluid limits at this "
                 "stage are individually prescribed; NutriMe must not guess.")),
        # -- refuse-tier conditions that fell through to disclaimer (#58) --
        (r"\b(decompensat|hepatic\s+encephalopath|ascites|variceal|varices)",
         _c("decompensated cirrhosis", REFUSE,
            ("a hepatologist", "the transplant team"),
            note="Decompensated liver disease needs specialist-set protein, "
                 "sodium and fluid targets; NutriMe must not guess.")),
        (r"\b(pku|phenylketonuria|msud|maple\s+syrup\s+urine|urea.?cycle|"
         r"galactosemia|glycogen\s+storage|mcad|fatty\s+acid\s+oxidation|"
         r"inborn\s+error)",
         _c("hereditary metabolic disorder", REFUSE,
            ("a metabolic-disease / genetics team", "a metabolic RDN"),
            note="Hereditary metabolic disorders are managed with precise, "
                 "prescribed dietary formulas — metabolic-team territory "
                 "only.")),
        (r"\b(cystic\s+fibrosis|\bcf\s+(team|clinic|patient))",
         _c("cystic fibrosis", REFUSE,
            ("the CF care team", "a CF-specialized RDN"),
            note="CF nutrition (high-energy targets, enzyme timing, "
                 "fat-soluble vitamins) belongs with the CF team.")),
        (r"\b(acute\s+kidney|aki\b)",
         _c("acute kidney injury", REFUSE,
            ("the treating (inpatient) team", "a nephrologist"),
            note="Nutrition during the acute phase is managed by the "
                 "treating team.")),
        (r"\bshort\s+bowel",
         _c("short bowel syndrome", REFUSE,
            ("a GI / intestinal-failure team", "a nutrition-support RDN"),
            note="Short bowel nutrition is specialist-team territory.")),
        (r"\b(ketogenic|keto)\s+(diet\s+)?(for|therapy).{0,20}(epilep|seizure)|"
         r"\b(epilep|seizure).{0,30}(ketogenic|keto\b)|\bmedical\s+keto",
         _c("medical ketogenic diet", REFUSE,
            ("the neurology / keto team", "a keto-trained RDN"),
            note="Therapeutic ketogenic diets for epilepsy are prescribed "
                 "and ratio-controlled by the neuro-keto team.")),
        (r"\b(palliative|hospice|end.?of.?life)",
         _c("palliative / end-of-life care", REFUSE,
            ("the palliative-care team",),
            note="Comfort-focused nutrition is guided by the palliative "
                 "team, not a meal planner.")),
        (r"\b(cachexia)",
         _c("cancer cachexia", REFUSE,
            ("the oncology team", "an oncology RDN"),
            note="Cachexia needs specialist nutrition support.")),
        (r"\b(hyperemesis)",
         _c("hyperemesis gravidarum", REFUSE,
            ("the obstetric team",),
            note="Hyperemesis needs medical management — often IV fluids "
                 "and antiemetics — before meal planning helps.")),
        (r"\b(dka.?prone|brittle\s+diabet)",
         _c("brittle / DKA-prone diabetes", REFUSE,
            ("an endocrinologist", "a CDCES"),
            note="DKA-prone diabetes needs specialist-team management.")),
        # FTT with active coordination gates per the §2 table ("Gate —
        # pediatric RDN coordination"); a bare disclosure still refuses
        # below, since the dangerous case is unassessed faltering.
        (r"\b(failure\s+to\s+thrive|faltering\s+growth).{0,50}\b(pediatric|"
         r"paediatric)?\s*(rdn|dietitian|pediatrician|coordinat)|"
         r"\b(rdn|dietitian|pediatrician).{0,40}(failure\s+to\s+thrive|"
         r"faltering\s+growth)",
         _c("failure to thrive (team-coordinated)", GATE,
            ("a pediatrician", "a pediatric RDN"),
            plan_note="a child eater is on a supervised catch-up-growth "
                      "plan — favor energy-dense, protein-forward meals "
                      "the family shares",
            note="Proceeding alongside the pediatric team's "
                 "catch-up-growth framework.")),
        (r"\b(failure\s+to\s+thrive|faltering\s+growth)",
         _c("failure to thrive", REFUSE,
            ("a pediatrician", "a pediatric RDN"),
            note="Growth faltering needs pediatric assessment before an "
                 "app plans meals. If a pediatric RDN is already "
                 "coordinating, say so in the disclosure and NutriMe "
                 "proceeds with energy-dense family-meal rails.")),
        # -- pediatric enumeration (#46 / sweep #10 §2; kids as eaters) ----
        # Pediatric ARFID/EDs, T1D, celiac, CF, inborn errors, short
        # bowel, medical keto and oncology-in-treatment already match
        # the patterns above; these entries cover the pediatric rows
        # whose behavior DIFFERS from the adult default or that no
        # adult pattern matches at all. assume-add posture per scope.md.
        (_PED + r".{0,40}\b(cancer|leukemi|lymphoma|oncolog|tumou?r|"
         r"neuroblastoma|wilms)|"
         r"\b(cancer|leukemi|lymphoma|oncolog)\w*.{0,30}" + _PED,
         _c("pediatric oncology", REFUSE,
            ("the pediatric oncology team", "a pediatric oncology RDN"),
            note="Nutrition during childhood cancer care is managed by "
                 "the pediatric oncology team.")),
        (_PED + r".{0,40}\b(liver\s+disease|cirrhosis|hepatic)|"
         r"\b(biliary\s+atresia|alagille|kasai)",
         _c("pediatric chronic liver disease", REFUSE,
            ("a pediatric hepatologist",),
            note="Pediatric liver disease needs hepatology-set nutrition "
                 "targets; NutriMe must not guess.")),
        (_PED + r".{0,40}\b(crohn|colitis|ibd|inflammatory\s+bowel)"
         r".{0,50}\b(gi\b|gastro|coordinat|care\s+team)|"
         r"\b(crohn|colitis|ibd).{0,30}" + _PED +
         r".{0,50}\b(gi\b|gastro|coordinat|care\s+team)",
         _c("pediatric IBD (GI-coordinated)", GATE,
            ("a pediatric gastroenterologist", "a pediatric IBD RDN"),
            plan_note="a child eater manages inflammatory bowel disease "
                      "with their GI team — keep meals gentle and "
                      "consistent with the team's current phase guidance",
            note="Proceeding alongside the pediatric GI team.")),
        (_PED + r".{0,40}\b(crohn|colitis|\bibd\b|inflammatory\s+bowel)|"
         r"\b(crohn|colitis|\bibd\b|inflammatory\s+bowel).{0,30}" + _PED,
         _c("pediatric IBD", REFUSE,
            ("a pediatric gastroenterologist", "a pediatric IBD RDN"),
            note="Pediatric IBD nutrition (including exclusive enteral "
                 "nutrition for Crohn's) is GI-team territory. If a "
                 "pediatric GI team is coordinating, say so in the "
                 "disclosure and NutriMe proceeds with gentle rails.")),
        (_PED + r".{0,40}\b(kidney|renal|nephrotic|nephropathy)"
         r".{0,50}\b(nephrolog|coordinat|care\s+team)|"
         r"\b(nephrotic|kidney).{0,30}" + _PED +
         r".{0,50}\b(nephrolog|coordinat|care\s+team)",
         _c("pediatric kidney condition (nephrology-coordinated)", GATE,
            ("a pediatric nephrologist", "a pediatric renal RDN"),
            plan_note="a child eater has a kidney condition managed with "
                      "their nephrology team — go easy on potassium- and "
                      "phosphorus-heavy meals and keep sodium modest",
            note="Proceeding alongside the pediatric nephrology team's "
                 "targets.")),
        (_PED + r".{0,40}\b(kidney|renal|nephrotic|nephropathy)|"
         r"\bnephrotic\s+syndrome",
         _c("pediatric kidney condition", REFUSE,
            ("a pediatric nephrologist", "a pediatric renal RDN"),
            note="Potassium, phosphorus, protein and growth targets in "
                 "pediatric kidney disease are individually prescribed. "
                 "If pediatric nephrology is coordinating, say so in "
                 "the disclosure and NutriMe proceeds with gentle "
                 "rails.")),
        (r"\b(eosinophilic\s+esophagitis|\beoe\b).{0,50}\b(gi\b|gastro|"
         r"allerg|coordinat|care\s+team|elimination)",
         _c("eosinophilic esophagitis (team-coordinated)", GATE,
            ("a gastroenterologist", "an allergist", _RDN),
            plan_note="an eater follows a supervised elimination diet "
                      "for eosinophilic esophagitis — strictly exclude "
                      "the foods their team has eliminated (declared in "
                      "the avoid list)",
            note="Proceeding alongside the GI/allergy team's elimination "
                 "protocol — keep the avoid-foods list current with it.")),
        (r"\b(eosinophilic\s+esophagitis|\beoe\b)",
         _c("eosinophilic esophagitis", REFUSE,
            ("a gastroenterologist", "an allergist", _RDN),
            note="EoE elimination diets are staged and biopsy-guided — "
                 "GI/allergy-team territory. If the team is "
                 "coordinating, say so in the disclosure and keep the "
                 "avoid-foods list current with the protocol.")),
        # Negated coordination refuses (#58): "type 1 diabetes, no
        # endocrinologist" must not match the with-coordination gate
        # below just because the word "endocrinologist" appears.
        (r"\b(t1d|type\s*1\s*diabet).{0,40}\b(no|not|without|don.?t|"
         r"doesn.?t|haven.?t|can.?t|lost|lack|looking\s+for|need)"
         r"\b.{0,30}(endocrinolog|coordinat|care\s+team)",
         _c("type 1 diabetes", REFUSE,
            ("an endocrinologist",
             "a certified diabetes care and education specialist (CDCES)"),
            note="Type 1 planning needs endocrinologist coordination. If that "
                 "is in place, edit the disclosure to say so (e.g. \"type 1 "
                 "diabetes, coordinated with endocrinologist\") and NutriMe "
                 "will proceed with carb-counting rails.")),
        (r"\b(t1d|type\s*1\s*diabet).{0,40}(endocrinolog|coordinat|care\s+team)",
         _c("type 1 diabetes (endocrinologist-coordinated)", GATE,
            ("an endocrinologist",
             "a certified diabetes care and education specialist (CDCES)"),
            plan_note="an eater counts carbohydrates with their care team — "
                      "favor meals with clear, steady carbohydrate content",
            note="Proceeding alongside the endocrinologist's carb framework.")),
        (r"\b(t1d|type\s*1\s*diabet)",
         _c("type 1 diabetes", REFUSE,
            ("an endocrinologist",
             "a certified diabetes care and education specialist (CDCES)"),
            note="Type 1 planning needs endocrinologist coordination. If that "
                 "is in place, edit the disclosure to say so (e.g. \"type 1 "
                 "diabetes, coordinated with endocrinologist\") and NutriMe "
                 "will proceed with carb-counting rails.")),
        # -- gate --------------------------------------------------------------
        # Transplant before the general kidney pattern: "kidney
        # transplant" must not read as early-stage CKD (#58 — the
        # tacrolimus/cyclosporine + grapefruit interaction is the point).
        (r"\b(kidney|renal|liver|heart|organ)\s+transplant|"
         r"\btransplant.{0,25}(kidney|renal|liver|heart)|"
         r"\b(tacrolimus|cyclosporine|immunosuppress)",
         _c("organ transplant (immunosuppressed)", GATE,
            ("the transplant team", _RDN),
            plan_note="an eater takes transplant immunosuppressants — "
                      "exclude grapefruit and pomelo entirely, and favor "
                      "thoroughly-cooked food-safety-conservative meals",
            note="Immunosuppressant rails: no grapefruit/pomelo, strict "
                 "food-safety tilt, alongside the transplant team.")),
        (r"\b(ckd|chronic\s+kidney|kidney\s+disease)",
         _c("chronic kidney disease (early stage)", GATE,
            ("a nephrologist", "a renal RDN"),
            plan_note="an eater manages early kidney disease — go easy on "
                      "potassium- and phosphorus-heavy meals and very high protein",
            note="Early-stage CKD: plans tilt away from potassium/phosphorus-"
                 "heavy meals.")),
        (r"\bgestational\s+diabet",
         _c("gestational diabetes", GATE,
            ("the maternal-fetal medicine / obstetric team", "a CDCES"),
            plan_note="an eater has gestational diabetes — favor "
                      "carbohydrate-conscious, low-added-sugar meals",
            note="Plans favor carb-conscious meals alongside the obstetric "
                 "team's guidance.")),
        (r"\b(celiac|coeliac)",
         _c("celiac disease", GATE,
            ("a gastroenterologist", _RDN),
            plan_note="an eater has celiac disease — gluten must be strictly "
                      "avoided, including hidden sources",
            note="Strict gluten avoidance is enforced like an allergy.")),
        # -- pediatric gate tier (#46 / sweep #10 §2) -------------------------
        # Pediatric T2D gates where the adult default is disclaimer —
        # must sit above the general t2d pattern.
        (_PED + r".{0,40}\b(t2d|type\s*2\s*diabet)|"
         r"\b(t2d|type\s*2\s*diabet)\w*.{0,30}" + _PED,
         _c("pediatric type 2 diabetes", GATE,
            ("a pediatric endocrinologist", "a CDCES"),
            plan_note="a child eater manages type 2 diabetes — favor "
                      "lower-added-sugar, carbohydrate-conscious family "
                      "meals",
            note="Pediatric type 2 diabetes: plans gate on carb-conscious "
                 "meals alongside the pediatric endocrinology team.")),
        (r"\b(cow.?s?\s+milk\s+protein\s+allerg|\bcmpa\b|\bfpies\b|"
         r"food\s+protein.?induced\s+enterocolitis)",
         _c("cow's milk protein allergy / FPIES", GATE,
            ("a pediatric allergist", "a pediatric gastroenterologist"),
            plan_note="a child eater has a food-protein allergy managed "
                      "with their allergy team — strictly exclude the "
                      "trigger foods (declared in the allergen/avoid "
                      "lists) including hidden and cross-contact sources",
            note="Trigger foods are enforced like allergens; formula "
                 "choice and reintroduction timing stay with the "
                 "allergy team.")),
        (r"\b(fpiap|allergic\s+proctocolitis)",
         _c("food protein-induced allergic proctocolitis", GATE,
            ("a pediatric allergist", "a pediatric gastroenterologist"),
            plan_note="an eater follows a supervised elimination for an "
                      "infant's allergic proctocolitis — strictly exclude "
                      "the eliminated foods (declared in the avoid list)",
            note="Maternal-elimination and formula decisions stay with "
                 "the allergy/GI team; the avoid list enforces them.")),
        (r"\b(red.?s\b|relative\s+energy\s+deficiency|athletic\s+triad|"
         r"female\s+athlete\s+triad)",
         _c("RED-S / relative energy deficiency", GATE,
            ("a sports-medicine clinician", "an adolescent-medicine "
             "clinician", _RDN),
            plan_note="an eater is restoring energy availability under "
                      "clinical guidance — favor energy-dense, "
                      "calcium- and iron-rich meals; never restrict",
            note="Energy-availability targets come from the sports-"
                 "medicine team; plans tilt energy-dense and never "
                 "restrict.")),
        (r"\b(dysphagia|cleft\s+palate|iddsi|texture.?modified)",
         _c("feeding / swallowing condition", GATE,
            ("the feeding team (SLP/OT)", "a pediatric RDN"),
            plan_note="an eater needs texture-aware meals per their "
                      "feeding team's current IDDSI level — favor "
                      "recipes that adapt to soft or pureed textures",
            note="Texture levels (IDDSI) come from the SLP assessment; "
                 "plans favor texture-adaptable meals.")),
        # -- proceed with disclaimer -------------------------------------------
        # Pediatric rows resolved to disclaimer by synthesis.md Tension
        # #9 (bounded-role): obesity (AAP 2023 controversy — family
        # meals, NO weight framing), autism food selectivity without
        # ARFID, typical picky eating, pediatric intolerances.
        (_PED + r".{0,40}\b(obesit|overweight|bmi)|"
         r"\b(obesit|overweight)\w*.{0,30}" + _PED,
         _c("pediatric weight management", DISCLAIMER,
            ("a pediatrician", "a pediatric RDN"),
            plan_note="a child eater's family wants supportive routines — "
                      "plan balanced family meals everyone shares; do NOT "
                      "frame anything around weight, calories, or "
                      "portions for the child",
            note="Per AAP 2023 and NutriMe's bounded role: plans are "
                 "family-appropriate balanced meals with no weight "
                 "framing — treatment decisions belong to the "
                 "pediatrician.")),
        (r"\b(autism|\basd\b|autistic).{0,50}\b(food|eat|selectiv|sensory|"
         r"picky|feeding)|"
         r"\b(food\s+selectivity|sensory\s+feeding)",
         _c("autism-related food selectivity", DISCLAIMER,
            ("a pediatrician", "a feeding team (OT/SLP)", _RDN),
            plan_note="an eater has sensory-driven food preferences — "
                      "favor familiar, predictable preparations and "
                      "introduce variety gently alongside accepted foods",
            note="Selectivity-aware framing: gentle variety, no pressure. "
                 "If ARFID is in the picture, that needs the feeding "
                 "team (and NutriMe steps back).")),
        (r"\b(picky\s+eat|selective\s+eat|food\s+neophobia)",
         _c("picky eating (typical)", DISCLAIMER,
            ("a pediatrician",),
            plan_note="a child eater is a picky eater — favor familiar "
                      "components served family-style so they can choose, "
                      "with new foods appearing low-pressure alongside",
            note="Satter division of responsibility: parents decide "
                 "what/when/where, the child decides whether/how much. "
                 "Plans favor family-style meals with safe familiar "
                 "components.")),
        (r"\b(lactose\s+intoleran|fructose\s+intoleran|fructose\s+"
         r"malabsorption|sucrase.?isomaltase|\bcsid\b)",
         _c("food intolerance", DISCLAIMER,
            ("a gastroenterologist", _RDN),
            plan_note="an eater has a carbohydrate intolerance — go easy "
                      "on the trigger (lactose or fructose loads) and "
                      "favor naturally low-trigger alternatives",
            note="Tolerance thresholds are individual — the avoid list "
                 "can hard-exclude specific foods if needed.")),
        (r"\b(t2d|type\s*2\s*diabet)",
         _c("type 2 diabetes", DISCLAIMER,
            ("an endocrinologist or primary-care clinician", "a CDCES", _RDN),
            plan_note="an eater manages type 2 diabetes — favor "
                      "lower-added-sugar, carbohydrate-conscious meals")),
        (r"\bpre.?diabet",
         _c("prediabetes", DISCLAIMER,
            ("a primary-care clinician", _RDN),
            plan_note="an eater is managing prediabetes — favor "
                      "lower-added-sugar, carbohydrate-conscious meals")),
        (r"\b(hypertension|high\s+blood\s+pressure)",
         _c("hypertension", DISCLAIMER,
            ("a cardiologist or primary-care clinician", _RDN),
            plan_note="an eater manages high blood pressure — favor "
                      "lower-sodium meals")),
        (r"\b(dyslipidemia|high\s+cholesterol|hyperlipidemia)",
         _c("dyslipidemia", DISCLAIMER,
            ("a cardiologist or primary-care clinician", _RDN),
            plan_note="an eater manages high cholesterol — favor meals lower "
                      "in saturated fat")),
        (r"\b(gerd|reflux|heartburn)",
         _c("GERD / reflux", DISCLAIMER,
            ("a gastroenterologist", _RDN),
            plan_note="an eater manages reflux — go easy on very spicy, "
                      "fried, or heavily acidic meals")),
        (r"\b(ibs|irritable\s+bowel)",
         _c("irritable bowel syndrome", DISCLAIMER,
            ("a gastroenterologist", _RDN))),
        (r"\b(crohn|ulcerative\s+colitis|ibd|inflammatory\s+bowel)",
         _c("inflammatory bowel disease", DISCLAIMER,
            ("a gastroenterologist", "an IBD-experienced RDN"))),
        (r"\bgout\b",
         _c("gout", DISCLAIMER,
            ("a rheumatologist or primary-care clinician", _RDN),
            plan_note="an eater manages gout — limit purine-heavy foods such "
                      "as organ meats and some seafood")),
        (r"\bpcos\b|polycystic\s+ovar",
         _c("PCOS", DISCLAIMER, ("an endocrinologist or gynecologist", _RDN))),
        (r"\b(hypothyroid|hyperthyroid|hashimoto|graves|thyroid)",
         _c("thyroid condition", DISCLAIMER, ("an endocrinologist",))),
        (r"\b(nafld|masld|fatty\s+liver)",
         _c("metabolic liver disease (NAFLD/MASLD)", DISCLAIMER,
            ("a hepatologist or gastroenterologist", _RDN))),
        (r"\b(osteoporosis|osteopenia)",
         _c("osteoporosis / osteopenia", DISCLAIMER,
            ("a primary-care clinician or endocrinologist", _RDN))),
    )
)

# Chips offered in the intake UI — common disclosures, phrased the way the
# matcher recognizes them. Free text is always accepted alongside.
COMMON_CONDITIONS: tuple[str, ...] = (
    "type 2 diabetes",
    "prediabetes",
    "high blood pressure",
    "high cholesterol",
    "celiac disease",
    "GERD / reflux",
    "IBS",
    "gout",
    "PCOS",
    "thyroid condition",
    "kidney disease",
    "type 1 diabetes",
)

_UNRECOGNIZED = ConditionInfo(
    canonical="",
    behavior=GATE,
    specialties=("your doctor", _RDN),
    note="Not in NutriMe's condition registry — plans proceed with a "
         "clear flag that this condition carries no special rails here; "
         "please confirm the plan approach with your care team.",
)


def classify(disclosure_text: str) -> ConditionInfo:
    """Deterministically classify one free-text disclosure.

    Unrecognized text fails CLOSED toward ``gate`` (#58): a clinical
    layer must not hand an unknown condition the least restrictive
    behavior. The gate surfaces the condition on every plan and refers
    out, rather than refusing outright — the registry can't tell "mild
    seasonal allergy" from something serious, so it asks instead of
    assuming either way.
    """
    text = disclosure_text.strip()
    for pattern, info in _REGISTRY:
        if pattern.search(text):
            return info
    return ConditionInfo(
        canonical=text.lower(),
        behavior=_UNRECOGNIZED.behavior,
        specialties=_UNRECOGNIZED.specialties,
        plan_note=(
            f"an eater disclosed \"{text}\", which NutriMe has no "
            "specific rails for — keep meals conservative and flag that "
            "their care team should confirm the plan"
        ),
        note=_UNRECOGNIZED.note,
    )


@dataclass(frozen=True)
class GateDecision:
    """The household's aggregate condition posture for plan generation."""

    refusals: tuple[ConditionInfo, ...] = ()
    plan_notes: tuple[str, ...] = ()          # injected into every crossing
    conditions: tuple[ConditionInfo, ...] = ()

    @property
    def refused(self) -> bool:
        return bool(self.refusals)

    def refusal_message(self) -> str:
        parts = []
        for info in self.refusals:
            who = " or ".join(info.specialties[:2])
            parts.append(
                f"{info.canonical}: {info.note} Conditions like this are "
                f"typically managed by {who} — NutriMe isn't provider-"
                f"affiliated; this is who to look for."
            )
        return (
            "NutriMe can't generate meal plans for this household right now. "
            + " ".join(parts)
            + " Recipe search and the pantry still work; plan generation "
            "resumes when the disclosure changes."
        )


def household_gates(
    conn: sqlite3.Connection, tenant_id: str
) -> GateDecision:
    """Aggregate every ACTIVE member's disclosed conditions into one
    household decision. Fail-closed: any refuse-level condition refuses."""
    from nutrime.intake.store import household_profiles

    refusals: list[ConditionInfo] = []
    notes: list[str] = []
    all_infos: list[ConditionInfo] = []
    seen: set[str] = set()
    for profile in household_profiles(conn, tenant_id).values():
        for raw in profile.conditions:
            info = classify(raw)
            if info.canonical in seen:
                continue
            seen.add(info.canonical)
            all_infos.append(info)
            if info.behavior == REFUSE:
                refusals.append(info)
            elif info.plan_note:
                notes.append(info.plan_note)
    return GateDecision(
        refusals=tuple(refusals),
        plan_notes=tuple(notes),
        conditions=tuple(all_infos),
    )
