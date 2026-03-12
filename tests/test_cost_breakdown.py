import pytest

from ScenarioPropertySelector import (
    build_cost_breakdown,
    calculate_staartkosten,
    format_cost_breakdown,
    format_cost_summary_message,
)


@pytest.mark.parametrize(
    ("label", "expected_quantity", "expected_source"),
    [
        ("Daken", 934.47, "HoeveelhedenDak"),
        ("Skelet", 9660.9, "HoeveelhedenSkelet"),
        ("Gevel dicht", 8650.93, "HoeveelhedenGevel"),
        ("Appartementen", 110.0, "HoeveelhedenAantalAppartementen"),
        ("Sloopkosten", 0.0, "HoeveelhedenSloop"),
    ],
)
def test_build_cost_breakdown_prefers_extracted_hoeveelheden_over_generic_totals(
    label,
    expected_quantity,
    expected_source,
):
    property_totals = {
        "HoeveelhedenDak": 934.47,
        "HoeveelhedenGevel": 8650.93,
        "HoeveelhedenSloop": 0.0,
        "HoeveelhedenSkelet": 9660.9,
        "HoeveelhedenAantalAppartementen": 110.0,
    }

    rows, _ = build_cost_breakdown([], property_totals, {})
    row = next(row for row in rows if row["label"] == label)

    assert row["quantity"] == expected_quantity
    assert row["quantity_source"] == expected_source


def test_ontsluiting_outputs_only_the_selected_variant():
    property_totals = {
        "HoeveelhedenOntsluiting": 934.43,
        "ObjectBvo": 1000.0,
    }

    rows_galerij, _ = build_cost_breakdown([], property_totals, {"ScenarioOntsluiting": "0:Galerij"})
    labels_galerij = {row["label"] for row in rows_galerij}
    assert "Galerij" in labels_galerij
    assert "Corridor" not in labels_galerij

    rows_corridor, _ = build_cost_breakdown([], property_totals, {"ScenarioOntsluiting": "1:Corridor"})
    labels_corridor = {row["label"] for row in rows_corridor}
    assert "Corridor" in labels_corridor
    assert "Galerij" not in labels_corridor


def test_hoofdtrappenhuis_en_lift_wordt_vermenigvuldigd_met_aantal_verdiepingen():
    property_totals = {
        "HoeveelhedenHoofdtrappenhuizenVerdiepingen": 8.0,
    }

    rows, _ = build_cost_breakdown([], property_totals, {"ScenarioLiften": "0:1 lift"})
    row = next(row for row in rows if row["label"] == "Hoofdtrappenhuis + lift")

    assert row["rate"] == 21318.0
    assert row["quantity"] == 8.0
    assert row["quantity_source"] == "HoeveelhedenHoofdtrappenhuizenVerdiepingen"
    assert row["total"] == 170544.0


@pytest.mark.parametrize("scenario_liften", [0, 0.0, "0", "0:1 lift"])
def test_hoofdtrappenhuis_en_lift_accepteert_numerieke_scenarioselectie(scenario_liften):
    property_totals = {
        "HoeveelhedenHoofdtrappenhuizenVerdiepingen": 55.0,
    }

    rows, _ = build_cost_breakdown([], property_totals, {"ScenarioLiften": scenario_liften})
    row = next(row for row in rows if row["label"] == "Hoofdtrappenhuis + lift")

    assert row["rate"] == 21318.0
    assert row["quantity"] == 55.0
    assert row["total"] == 1172490.0


def test_hoofdtrappenhuis_en_lift_gebruikt_standaardoptie_als_scenario_ontbreekt():
    property_totals = {
        "HoeveelhedenHoofdtrappenhuizenVerdiepingen": 55.0,
    }

    rows, _ = build_cost_breakdown([], property_totals, {})
    row = next(row for row in rows if row["label"] == "Hoofdtrappenhuis + lift")

    assert row["selected_index"] == 0
    assert row["rate"] == 21318.0
    assert row["quantity"] == 55.0
    assert row["total"] == 1172490.0


def test_calculate_staartkosten_vermenigvuldigt_stapsgewijs():
    steps, staartkosten_total, total_including_staartkosten = calculate_staartkosten(100.0)

    assert [step["label"] for step in steps] == [
        "Staartkosten 1",
        "Staartkosten 2",
        "Staartkosten 3",
        "Staartkosten 4",
        "Staartkosten 5",
        "Staartkosten 6",
        "Staartkosten 7",
    ]
    assert steps[0]["input_total"] == 100.0
    assert steps[0]["applied_amount"] == 5.0
    assert steps[0]["output_total"] == 105.0
    assert steps[1]["input_total"] == 105.0
    assert steps[1]["applied_amount"] == 2.63
    assert steps[1]["output_total"] == 107.63
    assert steps[-1]["output_total"] == 113.51
    assert staartkosten_total == 13.51
    assert total_including_staartkosten == 113.51


def test_format_cost_breakdown_toont_staartkosten_na_kostenuitleg():
    rows = [
        {
            "label": "Fundering",
            "variant": "vibro-palen",
            "scenario_property": "ScenarioFundering",
            "selected_index": 1,
            "cost_key": "HoeveelhedenFundering",
            "rate": 414.6,
            "unit": "m2bbo",
            "quantity": 10.0,
            "quantity_source": "HoeveelhedenFundering",
            "total": 4146.0,
        },
        {
            "label": "Sloopkosten",
            "variant": None,
            "scenario_property": None,
            "selected_index": None,
            "cost_key": None,
            "rate": 100.0,
            "unit": "m2bvo",
            "quantity": 5.0,
            "quantity_source": "HoeveelhedenSloop",
            "total": 500.0,
        },
    ]
    summary = {
        "total_bvo": 0.0,
        "total_gbo": 0.0,
        "total_bbo": 0.0,
        "apartment_count": 0.0,
        "building_layers": 0.0,
        "known_cost_total": 4646.0,
        "staartkosten_total": 627.28,
        "total_including_staartkosten": 5273.28,
    }

    formatted = format_cost_breakdown(rows, summary)

    assert "Kostenuitleg per onderdeel:" in formatted
    assert "Totaal bekende directe bouwkosten: 4646.00" in formatted
    assert "Staartkosten stapsgewijs:" in formatted
    assert "Staartkosten 1 (Nader te detaileren, 5.00%): 4646.00 + 232.30 = 4878.30" in formatted
    assert "Totaal staartkosten: 627.28" in formatted
    assert "Totaal inclusief staartkosten: 5273.28" in formatted


def test_format_cost_summary_message_toont_alleen_kerncijfers():
    summary = {
        "total_bvo": 1234.5,
        "total_gbo": 1111.0,
        "total_bbo": 1222.0,
        "apartment_count": 20.0,
        "building_layers": 6.0,
        "known_cost_total": 450000.0,
        "staartkosten_total": 60892.34,
        "total_including_staartkosten": 510892.34,
    }

    formatted = format_cost_summary_message(summary)

    assert formatted == (
        "Total ObjectBvo: 1234.50\n"
        "Totaal bekende directe bouwkosten: 450000.00\n"
        "Totaal inclusief staartkosten: 510892.34"
    )
