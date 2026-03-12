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
    "HoeveelhedenNoodrappenhuizen": {0: '9.709', 1: None, 2: None},
    "HoeveelhedenLiften":           {0: '31.651', 1: None, 2: None},
    "HoeveelhedenBergingen":        {0: '416.0',  1: None,    2: None},
    "HoeveelhedenFietsenstallingen": {0: '348.0', 1: None, 2: None},
    "HoeveelhedenScootmobielruimtes": {0: '348.0', 1: None, 2: None},
    "HoeveelhedenGemeenschappelijkRuimte": {0: '45.0', 1: None, 2: None},
    "HoeveelhedenSloop":          {0: '100',    1: None,    2: None},
    "HoeveelhedenBalkon":         {0: '5220',   1: None,    2: None},
    "HoeveelhedenSceanrioOntsluiting": {0: '56.0', 1: '145', 2: None},
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
