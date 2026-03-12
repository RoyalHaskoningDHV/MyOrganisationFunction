"""This module contains the function's business logic."""

from enum import Enum

from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from flatten import flatten_base
from GetModelInfo import summarize_model_properties
from ScenarioPropertySelector import build_cost_breakdown, format_cost_breakdown, get_scenario_costs


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
        description="Objects with this speckle_type will trigger a failure.",
    )
    whisper_message: SecretStr = Field(
        default=SecretStr(""),
        title="Whisper Message",
        description="A secret message for testing purposes.",
    )
    text_input: str = Field(
        title="Text Input",
        description="Values given in this field will be available with the `text_input` key.",
    )
    scalar_value: float = Field(
        default=25.0,
        title="Numerical value",
        description=(
            "Annotating a field and providing a default value will tell the Automate UI "
            "to treat the input field as a number"
        ),
    )
    selection: str = Field(
        default="default",
        title="Select an option",
        description=(
            "Specifying a value as the default will provide the UI with a drop-down "
            "selection, preselecting the default value."
        ),
        json_schema_extra={"examples": ["default", "option 2", "option 3"]},
    )
    read_only: str = Field(
        default="Placeholder",
        title="Disabled Input Field",
        description=(
            "Marking a field as readOnly will disable the UI input, which can be used "
            "to mock input UI for future revision or pass values specific to a function revision."
        ),
    )


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """Run the automate function."""
    version_root_object = automate_context.receive_version()
    all_objects = list(flatten_base(version_root_object))

    objects_with_forbidden_speckle_type = [
        obj
        for obj in all_objects
        if hasattr(obj, "speckle_type") and obj.speckle_type == function_inputs.forbidden_speckle_type
    ]
    count_forbidden = len(objects_with_forbidden_speckle_type)

    _, property_totals, scenario_kozijn_value, scenario_properties = summarize_model_properties(all_objects)
    cost_rows, cost_summary = build_cost_breakdown(all_objects, property_totals, scenario_properties)
    cost_breakdown_text = format_cost_breakdown(cost_rows, cost_summary)

    automate_context.attach_info_to_objects(
        category="Model Summary",
        affected_objects=all_objects[:200],
        message=cost_breakdown_text,
        metadata={
            "analysis_type": function_inputs.analysis_type.value,
            "forbidden_type": function_inputs.forbidden_speckle_type,
            "scanned_count": len(all_objects),
            "forbidden_count": count_forbidden,
            "total_object_bvo": round(property_totals.get("ObjectBvo", 0.0), 2),
            "total_object_gbo": round(property_totals.get("ObjectGbo", 0.0), 2),
            "scenario_kozijn_value": scenario_kozijn_value,
            "scenario_properties": scenario_properties,
            "cost_breakdown_rows": cost_rows,
            "cost_breakdown_summary": cost_summary,
            "text_input": function_inputs.text_input,
            "scalar_value": function_inputs.scalar_value,
        },
    )

    if count_forbidden > 0:
        automate_context.attach_error_to_objects(
            category=f"Forbidden speckle_type ({function_inputs.forbidden_speckle_type})",
            affected_objects=objects_with_forbidden_speckle_type,
            message=f"This project contains forbidden type: {function_inputs.forbidden_speckle_type}",
        )
        automate_context.mark_run_failed(
            "Automation failed: "
            f"Found {count_forbidden} forbidden object(s) of type "
            f"{function_inputs.forbidden_speckle_type}."
        )
        automate_context.set_context_view()
        return

    automate_context.mark_run_success(
        f"Scan completed. Checked {len(all_objects)} objects. No forbidden types found."
    )


def automate_function_without_inputs(automate_context: AutomationContext) -> None:
    """A function example without inputs."""
    del automate_context


if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)

    scenario_number = 1
    scenario_costs = get_scenario_costs(scenario_number)
    print(f"Scenario {scenario_number} costs:")
    for name, amount in scenario_costs:
        print(f"  {name}: {amount}")
