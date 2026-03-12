def summarize_model_properties(all_objects):
    unique_properties = set()
    property_totals = {}
    scenario_kozijn_value = None
    scenario_properties = {}
    for obj in all_objects:
        properties = getattr(obj, "properties", None)
        if properties:
            for property_name, property_value in properties.items():
                # Try to sum all numeric properties
                try:
                    value = float(property_value)
                    property_totals[property_name] = property_totals.get(property_name, 0.0) + value
                except (TypeError, ValueError):
                    pass
                # Collect all properties starting with 'Scenario'
                if property_name.startswith("Scenario"):
                    scenario_properties[property_name] = property_value
                unique_properties.add(property_name)
    for property_name in unique_properties:
        print(f"Property: {property_name}")
    print("Total sum for each property:")
    for property_name, total in property_totals.items():
        print(f"  {property_name}: {round(total, 2)}")
    print("All Scenario* properties found:")
    for k, v in scenario_properties.items():
        print(f"  {k}: {v}")
    return unique_properties, property_totals, scenario_kozijn_value, scenario_properties
