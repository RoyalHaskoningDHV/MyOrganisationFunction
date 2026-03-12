"""This module contains the function's business logic.

Use the automation_context module to wrap your function in an Automate context helper.
"""

from enum import Enum

from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)


from flatten import flatten_base
from GetModelInfo import summarize_model_properties
from ScenarioPropertySelector import get_scenario_costs, print_scenario_costs


class AnalysisType(str, Enum):
    STRUCTURAL = "structural"
    THERMAL = "thermal"
    COST = "cost"


class FunctionInputs(AutomateBase):
    analysis_type: AnalysisType = Field(
        default=AnalysisType.STRUCTURAL,
        title="Analysis Type",
        description="Select analysis method",
    )
    forbidden_speckle_type: str = Field(
        default="None",
        title="Forbidden Speckle Type",
        description="Objects with this speckle_type will trigger a failure."
    )
    whisper_message: SecretStr = Field(
        default=SecretStr(""),
        title="Whisper Message",
        description="A secret message for testing purposes."
    )
    text_input: str = Field(
        title="Text Input",
        description="Values given in this field will be available with the `text_input` key."
    )
    scalar_value: float = Field(
        default=25.0,
        title="Numerical value",
        description=("Annotating a field and providing a default value will tell the Automate UI to treat the input field as a number")
    )
    selection: str = Field(
        default="default",
        title="Select an option",
        description="Specifying a value as the default will provide the UI with a drop-down selection, preselecting the default value.",
        json_schema_extra={
            "examples": ["default", "option 2", "option 3"]
        }
    )
    read_only: str = Field(
        default="Placeholder",
        title="Disabled Input Field",
        description=("Marking a field as readOnly will disable the UI input, which can be used to mock input UI for future revision or pass values specific to a function revision.")
    )

    """This is an example Speckle Automate function.
    Args:
        automate_context: A context-helper object that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data that triggered this run.
            It also has convenient methods for attaching results to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """
def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:

    version_root_object = automate_context.receive_version()
    all_objects = list(flatten_base(version_root_object))

    objects_with_forbidden_speckle_type = [
        b
        for b in all_objects
        if hasattr(b, "speckle_type")
        and b.speckle_type == function_inputs.forbidden_speckle_type
    ]
    count_forbidden = len(objects_with_forbidden_speckle_type)

    # Summarize model properties using the new function
    unique_properties, property_totals, scenario_kozijn_value, scenario_properties = summarize_model_properties(all_objects)

    # Print costs for each scenario property and its selected index
    from ScenarioPropertySelector import get_cost_for_scenario_property
    if scenario_properties:
        print("Scenario property costs:")
        for prop, val in scenario_properties.items():
            # Try to extract the selected index from the value (e.g., '2:Houtbouw' -> 2)
            selected_index = None
            if isinstance(val, str) and ":" in val:
                try:
                    selected_index = int(val.split(":")[0].strip())
                except Exception:
                    selected_index = None
            if selected_index is not None:
                name, amount = get_cost_for_scenario_property(prop, selected_index)
                print(f"  {name} (selected index {selected_index}): {amount}", flush=True) 

    automate_context.attach_info_to_objects(
        category="Model Summary",
        affected_objects=all_objects[:200],
        message=(
            f"  • Total ObjectBvo: {round(property_totals.get('ObjectBvo', 0.0), 2)}\n"
            f"  • Total ObjectGbo: {round(property_totals.get('ObjectGbo', 0.0), 2)}\n"
            f"  •  {scenario_properties}\n"
        ),
        metadata={
            "analysis_type": function_inputs.analysis_type.value,
            "forbidden_type": function_inputs.forbidden_speckle_type,
            "scanned_count": len(all_objects),
            "forbidden_count": count_forbidden,
            "total_object_bvo": round(property_totals.get('ObjectBvo', 0.0), 2),
            "total_object_gbo": round(property_totals.get('ObjectGbo', 0.0), 2),
            "scenario_kozijn_value": scenario_kozijn_value,
            "scenario_properties": scenario_properties,
            "text_input": function_inputs.text_input,
            "scalar_value": function_inputs.scalar_value,
        },
    )

    if count_forbidden > 0:
        automate_context.attach_error_to_objects(
            category=f"Forbidden speckle_type ({function_inputs.forbidden_speckle_type})",
            affected_objects=objects_with_forbidden_speckle_type,
            message=(
                "This project contains forbidden type: "
                f"{function_inputs.forbidden_speckle_type}"
            ),
        )
        automate_context.mark_run_failed(
            "Automation failed: "
            f"Found {count_forbidden} forbidden object(s) of type "
            f"{function_inputs.forbidden_speckle_type}."
        )
        automate_context.set_context_view()
    else:
        automate_context.mark_run_success(
            f"Scan completed. Checked {len(all_objects)} objects. No forbidden types found."
        )

    # If the function generates file results, this is how it can be
    # attached to the Speckle project/model
    # automate_context.store_file_result("./report.pdf")


def automate_function_without_inputs(automate_context: AutomationContext) -> None:
    """A function example without inputs.

    If your function does not need any input variables,
     besides what the automation context provides,
     the inputs argument can be omitted.
    """
    pass


if __name__ == "__main__":
    # Speckle Automate runtime entrypoint
    execute_automate_function(automate_function, FunctionInputs)

    # Print scenario costs for demonstration
    scenario_number = 1
    scenario_costs = get_scenario_costs(scenario_number)
    print(f"Scenario {scenario_number} costs:")
    for name, amount in scenario_costs:
        print(f"  {name}: {amount}")
