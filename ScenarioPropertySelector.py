from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from GetModelInfo import summarize_model_properties
from InfoData import COST_ROW_DEFINITIONS, COST_TABLE, STAARTKOSTEN


def _safe_float(value: Any) -> float | None:
    """Convert numeric-like values to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        elif cleaned.count(".") == 1:
            whole, decimal = cleaned.split(".", maxsplit=1)
            if len(decimal) == 3 and whole.isdigit() and decimal.isdigit():
                cleaned = whole + decimal
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _extract_selected_index(value: Any) -> int | None:
    """Extract a scenario option index from values like `2:Houtbouw`."""
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        if ":" in cleaned:
            cleaned = cleaned.split(":", maxsplit=1)[0].strip()
        try:
            parsed_value = float(cleaned.replace(",", "."))
        except ValueError:
            return None
        return int(parsed_value) if parsed_value.is_integer() else None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def get_cost_for_scenario_property(scenario_property: str, selected_index: int) -> tuple[str, str | None]:
    """Return the chosen cost-table value for a scenario property."""
    import re

    suffix = re.sub(r"(?i)^scenario", "", scenario_property)
    suffix = re.sub(r"(?i)^variant", "", suffix).strip("_")
    hoeveelheden_key = "Hoeveelheden" + suffix

    if hoeveelheden_key in COST_TABLE:
        cost_entry = COST_TABLE[hoeveelheden_key]
        if selected_index in cost_entry and cost_entry[selected_index] is not None:
            return hoeveelheden_key, cost_entry[selected_index]

    suffix_lower = suffix.lower()
    for key, cost_entry in COST_TABLE.items():
        if suffix_lower and suffix_lower in key.lower():
            if selected_index in cost_entry and cost_entry[selected_index] is not None:
                return key, cost_entry[selected_index]

    return hoeveelheden_key, None


def process_scenario_properties(all_objects):
    """Split scenario properties into numeric and text maps."""
    _, _, _, scenario_properties = summarize_model_properties(all_objects)
    numbers = {}
    texts = {}
    for key, value in scenario_properties.items():
        try:
            numbers[key] = float(value)
        except (ValueError, TypeError):
            texts[key] = value
    return numbers, texts


def get_scenario_costs(scenario_number: int) -> list[tuple[str, str]]:
    """Return the configured unit rates for a scenario number."""
    results = []
    for key, values in COST_TABLE.items():
        if scenario_number in values and values[scenario_number] is not None:
            name = key[len("Hoeveelheden"):] if key.startswith("Hoeveelheden") else key
            results.append((name, values[scenario_number]))
    return results


def _derive_model_quantities(all_objects, property_totals: dict[str, float]) -> dict[str, float]:
    """Build a quantity dictionary with direct totals and practical fallbacks."""
    quantities = dict(property_totals)

    apartment_count = None
    for candidate in (
        "HoeveelhedenAantalAppartementen",
        "AantalAppartementen",
        "AantalWoningen",
        "ObjectAantalAppartementen",
        "ObjectAantalWoningen",
    ):
        value = _safe_float(property_totals.get(candidate))
        if value is not None:
            apartment_count = value
            break
    if apartment_count is None:
        apartment_count = float(
            sum(1 for obj in all_objects if _safe_float(getattr(obj, "properties", {}).get("ObjectGbo")) not in (None, 0.0))
        )

    building_layers = None
    for candidate in (
        "HoeveelhedenHoofdtrappenhuizenVerdiepingen",
        "HoeveelhedenNoodtrappenhuizenVerdiepingen",
        "AantalBouwlagen",
        "Bouwlagen",
        "ObjectBouwlagen",
    ):
        value = _safe_float(property_totals.get(candidate))
        if value is not None:
            building_layers = value
            break

    quantities["AantalAppartementen"] = apartment_count
    quantities["AantalWoningen"] = apartment_count
    if apartment_count is not None:
        quantities["HoeveelhedenAantalAppartementen"] = apartment_count
    if building_layers is not None:
        quantities["AantalBouwlagen"] = building_layers
        quantities["Bouwlagen"] = building_layers
    return quantities


def _resolve_quantity(row: dict[str, Any], quantities: dict[str, float]) -> tuple[float | None, str | None]:
    """Pick the first available model quantity for a row."""
    for key in row.get("quantity_keys", []):
        value = _safe_float(quantities.get(key))
        if value is not None:
            return value, key
    return None, None


def _round_currency(value: float) -> float:
    """Round currency values with the conventional half-up strategy."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_staartkosten(base_total: float) -> tuple[list[dict[str, Any]], float, float]:
    """Apply staartkosten percentages cumulatively to a base amount."""
    running_total = _round_currency(base_total)
    steps = []

    for label, description, percentage_text in STAARTKOSTEN:
        percentage = _safe_float(percentage_text) or 0.0
        applied_amount = _round_currency(running_total * (percentage / 100.0))
        new_total = _round_currency(running_total + applied_amount)
        steps.append(
            {
                "label": label,
                "description": description,
                "percentage": percentage,
                "input_total": running_total,
                "applied_amount": applied_amount,
                "output_total": new_total,
            }
        )
        running_total = new_total

    staartkosten_total = _round_currency(running_total - _round_currency(base_total))
    return steps, staartkosten_total, running_total


def build_cost_breakdown(
    all_objects,
    property_totals: dict[str, float],
    scenario_properties: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """Build a transparent cost breakdown from model quantities and scenario selections."""
    quantities = _derive_model_quantities(all_objects, property_totals)
    rows = []

    for row_definition in COST_ROW_DEFINITIONS:
        quantity, quantity_source = _resolve_quantity(row_definition, quantities)
        scenario_property = row_definition.get("scenario_property")
        selected_index = _extract_selected_index(scenario_properties.get(scenario_property)) if scenario_property else None
        if selected_index is None:
            selected_index = row_definition.get("default_selected_index")
        active_selected_indices = row_definition.get("active_selected_indices")

        if active_selected_indices is not None and selected_index not in active_selected_indices:
            continue

        variant = None
        rate = row_definition.get("rate")
        cost_key = row_definition.get("cost_key")
        if cost_key and selected_index is not None:
            raw_rate = COST_TABLE.get(cost_key, {}).get(selected_index)
            parsed_rate = _safe_float(raw_rate)
            if parsed_rate is not None:
                rate = parsed_rate
            variant = row_definition.get("variant_labels", {}).get(selected_index) or scenario_properties.get(scenario_property)

        if variant is None and row_definition.get("variant_labels") and selected_index is not None:
            variant = row_definition["variant_labels"].get(selected_index)

        total = round(rate * quantity, 2) if rate is not None and quantity is not None else None
        rows.append(
            {
                "label": row_definition["label"],
                "variant": variant,
                "scenario_property": scenario_property,
                "selected_index": selected_index,
                "cost_key": cost_key,
                "rate": rate,
                "unit": row_definition["unit"],
                "quantity": quantity,
                "quantity_source": quantity_source,
                "total": total,
            }
        )

    known_cost_total = round(sum(row["total"] for row in rows if row["total"] is not None), 2)
    _, staartkosten_total, total_including_staartkosten = calculate_staartkosten(known_cost_total)

    summary = {
        "total_bvo": round(_safe_float(quantities.get("ObjectBvo")) or 0.0, 2),
        "total_gbo": round(_safe_float(quantities.get("ObjectGbo")) or 0.0, 2),
        "total_bbo": round(_safe_float(quantities.get("ObjectBbo")) or 0.0, 2),
        "apartment_count": round(_safe_float(quantities.get("AantalAppartementen")) or 0.0, 2),
        "building_layers": round(_safe_float(quantities.get("AantalBouwlagen")) or 0.0, 2),
        "known_cost_total": known_cost_total,
        "staartkosten_total": staartkosten_total,
        "total_including_staartkosten": total_including_staartkosten,
    }
    return rows, summary


def format_cost_breakdown(rows: list[dict[str, Any]], summary: dict[str, float]) -> str:
    """Render the cost breakdown into a concise readable text block."""
    staartkosten_steps, staartkosten_total, total_including_staartkosten = calculate_staartkosten(
        summary["known_cost_total"]
    )
    lines = [
        f"Total ObjectBvo: {summary['total_bvo']}",
        f"Total ObjectGbo: {summary['total_gbo']}",
        f"Total ObjectBbo: {summary['total_bbo']}",
        f"Aantal appartementen: {summary['apartment_count']}",
        f"Aantal bouwlagen: {summary['building_layers']}",
        "",
        "Kostenuitleg per onderdeel:",
    ]
    for row in rows:
        variant = f" [{row['variant']}]" if row["variant"] else ""
        rate_text = f"{row['rate']:.2f}" if row["rate"] is not None else "n.v.t."
        quantity_text = f"{row['quantity']:.2f}" if row["quantity"] is not None else "n.v.t."
        total_text = f"{row['total']:.2f}" if row["total"] is not None else "n.v.t."
        quantity_source = row["quantity_source"] or "geen modelwaarde gevonden"
        selection_text = (
            f", scenario={row['scenario_property']} -> optie {row['selected_index']}"
            if row["scenario_property"] and row["selected_index"] is not None
            else ""
        )
        lines.append(
            f"- {row['label']}{variant}: {rate_text} per {row['unit']} x {quantity_text} "
            f"(bron: {quantity_source}{selection_text}) = {total_text}"
        )
    lines.append("")
    lines.append(f"Totaal bekende directe bouwkosten: {summary['known_cost_total']:.2f}")
    lines.append("Staartkosten stapsgewijs:")
    for step in staartkosten_steps:
        lines.append(
            f"- {step['label']} ({step['description']}, {step['percentage']:.2f}%): "
            f"{step['input_total']:.2f} + {step['applied_amount']:.2f} = {step['output_total']:.2f}"
        )
    lines.append(f"Totaal staartkosten: {staartkosten_total:.2f}")
    lines.append(f"Totaal inclusief staartkosten: {total_including_staartkosten:.2f}")
    return "\n".join(lines)


def format_cost_summary_message(summary: dict[str, float]) -> str:
    """Render only the key totals for the main automation message."""
    return "\n".join(
        [
            f"Total ObjectBvo: {summary['total_bvo']:.2f}",
            f"Totaal bekende directe bouwkosten: {summary['known_cost_total']:.2f}",
            f"Totaal inclusief staartkosten: {summary['total_including_staartkosten']:.2f}",
        ]
    )


if __name__ == "__main__":
    all_objects = []
    numbers, texts = process_scenario_properties(all_objects)
    print("Scenario properties (numbers):")
    for key, value in numbers.items():
        print(f"  {key}: {value}")
    print("Scenario properties (text):")
    for key, value in texts.items():
        print(f"  {key}: {value}")
