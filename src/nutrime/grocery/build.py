"""Plan → grocery list assembly + export (6.1).

Reads a plan's filled slots (``parse_plan_body`` is the designed 5.4→6.1
hand-off), pulls each recipe's ingredients from the vault, aggregates,
nets against inventory presence, and renders. Export: plain text
(checklist, aisle-agnostic at MVP — food-category aisle grouping is the
sweep #16 follow-up once a food seed list exists) and markdown.
"""

from __future__ import annotations

from dataclasses import dataclass

from nutrime.grocery.aggregate import (
    GroceryLine,
    aggregate,
    display_amount,
    needs_from_recipe_body,
)
from nutrime.plans.store import PlanRecord
from nutrime.recipes.store import RecipeVault


@dataclass(frozen=True)
class GroceryList:
    plan_id: str
    lines: tuple[GroceryLine, ...]
    missing_recipe_ids: tuple[str, ...]  # slots whose recipe left the vault

    @property
    def to_buy(self) -> tuple[GroceryLine, ...]:
        return tuple(l for l in self.lines if not l.on_hand)

    @property
    def have(self) -> tuple[GroceryLine, ...]:
        return tuple(l for l in self.lines if l.on_hand)


def build_grocery_list(
    plan: PlanRecord,
    vault: RecipeVault,
    *,
    inventory_names: list[str] | tuple[str, ...] = (),
) -> GroceryList:
    needs = []
    missing: list[str] = []
    seen: set[str] = set()
    for entry in plan.entries():
        if not entry.filled or entry.recipe_id in seen:
            continue
        seen.add(entry.recipe_id)
        try:
            record = vault.read(entry.recipe_id)
        except OSError:
            missing.append(entry.recipe_id)
            continue
        needs.append(
            needs_from_recipe_body(
                entry.recipe_id,
                str(record.frontmatter.get("title", entry.title)),
                record.body,
            )
        )
    lines = aggregate(needs, inventory_names=inventory_names)
    return GroceryList(
        plan_id=plan.plan_id,
        lines=tuple(lines),
        missing_recipe_ids=tuple(missing),
    )


def render_text(groceries: GroceryList) -> str:
    """Plain-text checklist — the universal export (paste anywhere)."""
    out: list[str] = []
    out.append(f"Grocery list — plan {groceries.plan_id}")
    out.append("")
    for line in groceries.to_buy:
        amount = display_amount(line)
        label = f"{amount} {line.food}".strip()
        note = f"  ({'; '.join(line.notes)})" if line.notes else ""
        recipes = {c.recipe_title for c in line.contributions}
        out.append(f"[ ] {label}{note}  — for: {', '.join(sorted(recipes))}")
    if groceries.have:
        out.append("")
        out.append("Already have (check your kitchen):")
        for line in groceries.have:
            amount = display_amount(line)
            out.append(f"[x] {f'{amount} {line.food}'.strip()}")
    if groceries.missing_recipe_ids:
        out.append("")
        out.append(
            "! Some planned recipes are no longer in the vault:"
            f" {', '.join(groceries.missing_recipe_ids)}"
        )
    return "\n".join(out) + "\n"


def render_markdown(groceries: GroceryList) -> str:
    out: list[str] = []
    out.append(f"# Grocery list — plan {groceries.plan_id}")
    out.append("")
    out.append("## To buy")
    for line in groceries.to_buy:
        amount = display_amount(line)
        label = f"**{line.food}**" + (f" — {amount}" if amount else "")
        note = f" _({'; '.join(line.notes)})_" if line.notes else ""
        recipes = {c.recipe_title for c in line.contributions}
        out.append(f"- [ ] {label}{note} · for: {', '.join(sorted(recipes))}")
    if groceries.have:
        out.append("")
        out.append("## Already on hand")
        for line in groceries.have:
            amount = display_amount(line)
            out.append(f"- [x] {line.food}" + (f" — {amount}" if amount else ""))
    return "\n".join(out) + "\n"
