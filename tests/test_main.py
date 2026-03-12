from enum import Enum
from types import SimpleNamespace

import main


class FakeAnalysisType(Enum):
    COST = "cost"


class FakeAutomationContext:
    def __init__(self):
        self.info_message = None
        self.info_metadata = None
        self.success_message = None

    def receive_version(self):
        return object()

    def attach_info_to_objects(self, *, category, affected_objects, message, metadata):
        self.info_message = message
        self.info_metadata = metadata
        self.info_category = category
        self.affected_objects = affected_objects

    def mark_run_success(self, message):
        self.success_message = message

    def attach_error_to_objects(self, **kwargs):
        raise AssertionError(f"No error expected, got: {kwargs}")

    def mark_run_failed(self, message):
        raise AssertionError(f"Run should not fail: {message}")

    def set_context_view(self):
        raise AssertionError("Context view should not be set for a successful run")


def test_automate_function_prints_detailed_breakdown_and_attaches_summary(monkeypatch, capsys):
    monkeypatch.setattr(main, "flatten_base", lambda version_root_object: [])
    monkeypatch.setattr(main, "summarize_model_properties", lambda all_objects: ({}, {"ObjectBvo": 123.0}, None, {}))
    monkeypatch.setattr(main, "build_cost_breakdown", lambda all_objects, property_totals, scenario_properties: ([], {"total_bvo": 123.0, "known_cost_total": 456.0, "total_including_staartkosten": 789.0}))
    monkeypatch.setattr(main, "format_cost_breakdown", lambda cost_rows, cost_summary: "detailed breakdown")
    monkeypatch.setattr(main, "format_cost_summary_message", lambda cost_summary: "compact summary")

    automate_context = FakeAutomationContext()
    function_inputs = SimpleNamespace(
        forbidden_speckle_type="None",
        analysis_type=FakeAnalysisType.COST,
        text_input="hello",
        scalar_value=25.0,
    )

    main.automate_function(automate_context, function_inputs)

    captured = capsys.readouterr()

    assert "detailed breakdown" in captured.out
    assert automate_context.info_message == "compact summary"
    assert automate_context.info_metadata["cost_breakdown_summary"] == {
        "total_bvo": 123.0,
        "known_cost_total": 456.0,
        "total_including_staartkosten": 789.0,
    }
    assert automate_context.success_message == "Scan completed. Checked 0 objects. No forbidden types found."


def test_automate_function_attaches_more_than_200_objects(monkeypatch):
    objects = [object() for _ in range(500)]

    monkeypatch.setattr(main, "flatten_base", lambda version_root_object: objects)
    monkeypatch.setattr(main, "summarize_model_properties", lambda all_objects: ({}, {"ObjectBvo": 0.0}, None, {}))
    monkeypatch.setattr(main, "build_cost_breakdown", lambda all_objects, property_totals, scenario_properties: ([], {"total_bvo": 0.0, "known_cost_total": 0.0, "total_including_staartkosten": 0.0}))
    monkeypatch.setattr(main, "format_cost_breakdown", lambda cost_rows, cost_summary: "detailed breakdown")
    monkeypatch.setattr(main, "format_cost_summary_message", lambda cost_summary: "compact summary")

    automate_context = FakeAutomationContext()
    function_inputs = SimpleNamespace(
        forbidden_speckle_type="None",
        analysis_type=FakeAnalysisType.COST,
        text_input="hello",
        scalar_value=25.0,
    )

    main.automate_function(automate_context, function_inputs)

    assert len(automate_context.affected_objects) == len(objects)
    assert automate_context.affected_objects == objects
