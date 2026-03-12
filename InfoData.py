# InfoData.py
"""
Centralized data for scenario property costs and related constants.
"""

COST_TABLE = {
    "HoeveelhedenFundering":    {0: '282',    1: '414.6', 2: None},
    "HoeveelhedenSkelet":       {0: '230.1',  1: '214',   2: '541'},
    "HoeveelhedenDak":          {0: '259.9',  1: '334.9', 2: None},
    "HoeveelhedenGevel":        {0: '441.9',  1: None,    2: None},  
    "HoeveelhedenGevelOpeningen": {0: '915.2', 1: '1265.2', 2: None},
    "HoeveelhedenBinnenwanden": {0: '81.4',   1: None,    2: None},
    "HoeveelhedenVloeren":      {0: '31.6',   1: None,    2: None},
    "HoeveelhedenPlafonds":     {0: '17.6',   1: None,    2: None},
    "HoeveelhedenDiversen":     {0: '22.0',   1: None,    2: None},
    "HoeveelhedenVastelinrichting": {0: '26.0', 1: None, 2: None},
    "HoeveelhedenWerktuigbouwkundigeInstallaties": {0: '232.0', 1: '325.2', 2: '395.5'},
    "HoeveelhedenElektrischeInstallaties": {0: '137.0', 1: None, 2: None},
    "HoeveelhedenHoofdtrappenhuis + lift": {0: '21318', 1:'30422' , 2: None},
    "HoeveelhedenNoodtrappenhuizen": {0: '9.709', 1: '10333', 2: None},
    "HoeveelhedenLiften":           {0: '31.651', 1: None, 2: None},
    "HoeveelhedenBergingen":        {0: '416.0',  1: None,    2: None},
    "HoeveelhedenFietsenstallingen": {0: '348.0', 1: None, 2: None},
    "HoeveelhedenScootmobielruimtes": {0: '348.0', 1: None, 2: None},
    "HoeveelhedenGemeenschappelijkRuimte": {0: '45.0', 1: None, 2: None},
    "HoeveelhedenSloop":          {0: '100',    1: None,    2: None},
    "HoeveelhedenBalkon":         {0: '5220',   1: None,    2: None},
    "HoeveelhedenScenarioOntsluiting": {0: '56.0', 1: '145', 2: None},
    "HoeveelhedenAppartementenvierkantemeter": {0: '290.0', 1: None, 2: None},
}

STAARTKOSTEN = [
    ("Staartkosten 1", 'Nader te detaileren', '5.0'),
    ("Staartkosten 2", 'Algemene bouwplaatskosten', '2.5'),
    ("Staartkosten 3", 'Algemene kosten', '1.0'),
    ("Staartkosten 4", 'Winst en risico', '4.0'),
    ("Staartkosten 5", 'Prijsstijgingen tot start bouw', '0.0'),
    ("Staartkosten 6", 'Prijsstijgingen tijdens bouw', '0.0'),
    ("Staartkosten 7", 'CAR-verzekering', '0.4'),
]

OPPEX = []

COST_ROW_DEFINITIONS = [
    {
        "label": "Sloopkosten",
        "rate": 100.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenSloop", "ObjectBvo"],
    },
    {
        "label": "Fundering",
        "scenario_property": "ScenarioFundering",
        "cost_key": "HoeveelhedenFundering",
        "variant_labels": {
            0: "prefab heipalen",
            1: "vibro-palen",
        },
        "unit": "m2bbo",
        "quantity_keys": ["HoeveelhedenFundering", "ObjectBbo", "ObjectBvo"],
    },
    {
        "label": "Skelet",
        "scenario_property": "ScenarioSkelet",
        "cost_key": "HoeveelhedenSkelet",
        "variant_labels": {
            0: "beton",
            1: "Kalkzandsteen",
            2: "Hout",
        },
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenSkelet", "ObjectBvo"],
    },
    {
        "label": "Galerijconstructie",
        "rate": 56.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenOntsluiting", "ObjectBvo"],
    },
    {
        "label": "Balkonplaten",
        "rate": 5220.0,
        "unit": "won",
        "quantity_keys": ["HoeveelhedenAantalAppartementen", "AantalWoningen", "AantalAppartementen"],
    },
    {
        "label": "Daken",
        "scenario_property": "ScenarioDak",
        "cost_key": "HoeveelhedenDak",
        "variant_labels": {
            0: "standaard dak",
            1: "sedumdak",
        },
        "unit": "m2bbo",
        "quantity_keys": ["HoeveelhedenDak", "ObjectBbo", "ObjectBvo"],
    },
    {
        "label": "Gevel dicht",
        "rate": 441.9,
        "unit": "m2",
        "quantity_keys": ["HoeveelhedenGevel", "ObjectGevelOppervlakte", "GevelOppervlakte", "ObjectBvo"],
    },
    {
        "label": "Gevelopeningen",
        "scenario_property": "ScenarioGevelOpeningen",
        "cost_key": "HoeveelhedenGevelOpeningen",
        "variant_labels": {
            0: "Kunststof kozijnen HR+++",
            1: "Aluminium kozijnen HR+++",
            2: "Houten / Aluminium kozijnen HR+++",
        },
        "unit": "m2",
        "quantity_keys": ["HoeveelhedenGevelOpeningen", "ObjectGevelopeningen", "Gevelopeningen", "ObjectBvo"],
    },
    {
        "label": "Binnenwanden woning",
        "rate": 81.4,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenBinnenwanden", "ObjectBvo"],
    },
    {
        "label": "Vloeren",
        "rate": 31.6,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenVloeren", "ObjectBvo"],
    },
    {
        "label": "Hoofdtrappenhuis + lift",
        "scenario_property": "ScenarioLiften",
        "cost_key": "HoeveelhedenHoofdtrappenhuis + lift",
        "default_selected_index": 0,
        "variant_labels": {
            0: "1 lift",
        },
        "unit": "bouwlaag",
        "quantity_keys": ["HoeveelhedenHoofdtrappenhuizenVerdiepingen", "AantalBouwlagen", "Bouwlagen"],
    },
    {
        "label": "Noodtrappenhuis",
        "rate": 9709.0,
        "unit": "bouwlaag",
        "quantity_keys": ["HoeveelhedenNoodtrappenhuizenVerdiepingen", "AantalBouwlagen", "Bouwlagen"],
    },
    {
        "label": "Plafonds en overige afwerkingen",
        "rate": 18.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenPlafonds", "ObjectBvo"],
    },
    {
        "label": "Diversen",
        "rate": 22.0,
        "unit": "m2bvo",
        "quantity_keys": ["ObjectBvo"],
    },
    {
        "label": "W-installaties",
        "scenario_property": "ScenarioWerktuigbouwkundigeInstallaties",
        "cost_key": "HoeveelhedenWerktuigbouwkundigeInstallaties",
        "variant_labels": {
            0: "Collectief centrale opwekking",
            1: "Collectief per woning",
            2: "individueel",
        },
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenWerktuigbouwkundigeInstallaties", "ObjectBvo"],
    },
    {
        "label": "E-installaties",
        "rate": 137.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenElektrischeInstallaties", "ObjectBvo"],
    },
    {
        "label": "Vaste inrichting",
        "rate": 26.0,
        "unit": "m2bvo",
        "quantity_keys": ["ObjectBvo"],
    },
    {
        "label": "Fietsenberging",
        "rate": 348.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenFietsenstallingen", "ObjectFietsenbergingBvo", "FietsenbergingBvo", "ObjectBvo"],
    },
    {
        "label": "Corridor",
        "scenario_property": "ScenarioOntsluiting",
        "rate": 389.0,
        "unit": "m2bvo",
        "active_selected_indices": [1],
        "quantity_keys": ["HoeveelhedenOntsluiting", "ObjectCorridorBvo", "CorridorBvo", "ObjectBvo"],
    },
    {
        "label": "Galerij",
        "scenario_property": "ScenarioOntsluiting",
        "rate": 56.0,
        "unit": "m2bvo",
        "active_selected_indices": [0],
        "quantity_keys": ["HoeveelhedenOntsluiting", "ObjectGalerijBvo", "GalerijBvo", "ObjectBvo"],
    },
    {
        "label": "Bergingen",
        "rate": 416.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenBergingen", "ObjectBergingenBvo", "BergingenBvo", "ObjectBvo"],
    },
    {
        "label": "Gemeenschappelijke ruimte",
        "rate": 45.0,
        "unit": "m2bvo",
        "quantity_keys": ["HoeveelhedenScootmobielruimtes", "ObjectGemeenschappelijkeRuimteBvo", "GemeenschappelijkeRuimteBvo", "ObjectBvo"],
    },
    {
        "label": "Appartementen",
        "rate": 290.0,
        "unit": "appartement",
        "quantity_keys": ["HoeveelhedenAantalAppartementen", "AantalAppartementen", "AantalWoningen"],
    },
]
