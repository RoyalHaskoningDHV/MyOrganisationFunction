def print_scenario_costs_from_properties(scenario_properties):
    """
    Print costs for scenario properties that have a valid match in the cost table and a valid index.
    """
    print("Scenario property costs:")
    for prop, val in scenario_properties.items():
        selected_index = None
        if isinstance(val, str) and ":" in val:
            try:
                selected_index = int(val.split(":")[0].strip())
            except Exception:
                continue
        if selected_index is not None:
            name, amount = get_cost_for_scenario_property(prop, selected_index)
            if amount is not None:
                print(f"  {name} (selected index {selected_index}): {amount}")
def get_cost_for_scenario_property(scenario_property, selected_index):
    """
    Given a scenario property (e.g., 'ScenarioFundering') and a selected index (e.g., 2),
    return the corresponding cost from the COST_TABLE, using robust automatic mapping.
    """
    import re
    # Remove 'Scenario' and 'Variant' prefixes (case-insensitive)
    suffix = scenario_property
    suffix = re.sub(r'(?i)^scenario', '', suffix)
    suffix = re.sub(r'(?i)^variant', '', suffix)
    suffix = suffix.strip('_')
    # Try direct match
    hoeveelheden_key = 'Hoeveelheden' + suffix
    if hoeveelheden_key in COST_TABLE:
        cost_entry = COST_TABLE[hoeveelheden_key]
        if selected_index in cost_entry and cost_entry[selected_index] is not None:
            return hoeveelheden_key, cost_entry[selected_index]
    # Fuzzy match: look for any COST_TABLE key containing the suffix (case-insensitive)
    suffix_lower = suffix.lower()
    for k in COST_TABLE.keys():
        if suffix_lower and suffix_lower in k.lower():
            cost_entry = COST_TABLE[k]
            if selected_index in cost_entry and cost_entry[selected_index] is not None:
                return k, cost_entry[selected_index]
    return hoeveelheden_key, None
def print_scenario_costs(scenario_number):
    scenario_costs = get_scenario_costs(scenario_number)
    print(f"Scenario {scenario_number} costs:")
    for name, amount in scenario_costs:
        print(f"  {name}: {amount}")

from GetModelInfo import summarize_model_properties
from InfoData import COST_TABLE, STAARTKOSTEN, OPPEX

# Example usage: expects all_objects to be provided from main or another source
def process_scenario_properties(all_objects):
    _, _, _, scenario_properties = summarize_model_properties(all_objects)
    numbers = {}
    texts = {}
    for k, v in scenario_properties.items():
        try:
            num = float(v)
            numbers[k] = num
        except (ValueError, TypeError):
            texts[k] = v
    return numbers, texts


def get_scenario_costs(scenario_number):
    """
    Returns a list of (name, amount) tuples for the given scenario number
    from the COST_TABLE. The name is the part after 'Hoeveelheden'.
    """
    results = []
    for key, values in COST_TABLE.items():
        if scenario_number in values and values[scenario_number] is not None:
            # Extract the name after 'Hoeveelheden'
            if key.startswith("Hoeveelheden"):
                name = key[len("Hoeveelheden"):]
            else:
                name = key
            results.append((name, values[scenario_number]))
    return results

if __name__ == "__main__":
    all_objects = []
    numbers, texts = process_scenario_properties(all_objects)
    print("Scenario properties (numbers):")
    for k, v in numbers.items():
        print(f"  {k}: {v}")
    print("Scenario properties (text):")
    for k, v in texts.items():
        print(f"  {k}: {v}")

