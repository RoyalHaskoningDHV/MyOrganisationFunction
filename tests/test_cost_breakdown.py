from types import SimpleNamespace

from ScenarioPropertySelector import build_cost_breakdown


def test_build_cost_breakdown_uses_selected_scenario_and_model_quantities():
    all_objects = [
        SimpleNamespace(properties={"ObjectGbo": 50}),
        SimpleNamespace(properties={"ObjectGbo": 75}),
    ]
    property_totals = {
        "ObjectBvo": 1000.0,
        "ObjectGbo": 800.0,
        "ObjectBbo": 900.0,
        "AantalBouwlagen": 6.0,
    }
    scenario_properties = {
        "ScenarioFundering": "1:Vibro",
        "ScenarioSkelet": "2:Hout",
        "ScenarioDak": "1:Sedum",
        "ScenarioGevelOpeningen": "0:Kunststof",
        "ScenarioWerktuigbouwkundigeInstallaties": "2:Individueel",
        "ScenarioLiften": "0:Een lift",
    }

    rows, summary = build_cost_breakdown(all_objects, property_totals, scenario_properties)

    fundering = next(row for row in rows if row["label"] == "Fundering")
    assert fundering["rate"] == 414.6
    assert fundering["quantity"] == 900.0
    assert fundering["total"] == 373140.0

    skelet = next(row for row in rows if row["label"] == "Skelet")
    assert skelet["variant"] == "Hout"
    assert skelet["total"] == 541000.0

    appartementen = next(row for row in rows if row["label"] == "Appartementen")
    assert appartementen["quantity"] == 2.0
    assert appartementen["total"] == 580.0

    balkonplaten = next(row for row in rows if row["label"] == "Balkonplaten")
    assert balkonplaten["quantity"] == 2.0
    assert balkonplaten["total"] == 10440.0

    assert summary["known_cost_total"] > 0


def test_build_cost_breakdown_prefers_extracted_hoeveelheden_over_generic_totals():
    all_objects = []
    property_totals = {
        "ObjectBvo": 9999.0,
        "ObjectGbo": 8888.0,
        "ObjectBbo": 7777.0,
        "HoeveelhedenDak": 934.47,
        "HoeveelhedenGbo": 5759.55,
        "HoeveelhedenGevel": 8650.93,
        "HoeveelhedenSloop": 0.0,
        "HoeveelhedenSkelet": 9660.9,
        "HoeveelhedenVloeren": 9660.9,
        "HoeveelhedenPlafonds": 9660.9,
        "HoeveelhedenBergingen": 0.0,
        "HoeveelhedenFundering": 934.47,
        "HoeveelhedenOntsluiting": 934.43,
        "HoeveelhedenBinnenwanden": 7585.54,
        "HoeveelhedenGevelOpeningen": 2883.64,
        "HoeveelhedenFietsenstallingen": 0.0,
        "HoeveelhedenScootmobielruimtes": 91.0,
        "HoeveelhedenAantalAppartementen": 110.0,
        "HoeveelhedenElektrischeInstallaties": 9660.9,
        "HoeveelhedenNoodtrappenhuizenVerdiepingen": 0.0,
        "HoeveelhedenHoofdtrappenhuizenVerdiepingen": 33.0,
        "HoeveelhedenWerktuigbouwkundigeInstallaties": 9660.9,
    }
    scenario_properties = {
        "ScenarioFundering": "1:Vibro",
        "ScenarioSkelet": "2:Hout",
        "ScenarioDak": "1:Sedum",
        "ScenarioGevelOpeningen": "0:Kunststof",
        "ScenarioWerktuigbouwkundigeInstallaties": "2:Individueel",
        "ScenarioLiften": "0:Een lift",
    }

    rows, _ = build_cost_breakdown(all_objects, property_totals, scenario_properties)

    daken = next(row for row in rows if row["label"] == "Daken")
    assert daken["quantity"] == 934.47
    assert daken["quantity_source"] == "HoeveelhedenDak"

    skelet = next(row for row in rows if row["label"] == "Skelet")
    assert skelet["quantity"] == 9660.9
    assert skelet["quantity_source"] == "HoeveelhedenSkelet"

    gevel = next(row for row in rows if row["label"] == "Gevel dicht")
    assert gevel["quantity"] == 8650.93
    assert gevel["quantity_source"] == "HoeveelhedenGevel"

    appartementen = next(row for row in rows if row["label"] == "Appartementen")
    assert appartementen["quantity"] == 110.0
    assert appartementen["quantity_source"] == "HoeveelhedenAantalAppartementen"

    sloop = next(row for row in rows if row["label"] == "Sloopkosten")
    assert sloop["quantity"] == 0.0
    assert sloop["quantity_source"] == "HoeveelhedenSloop"


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
