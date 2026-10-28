"""No-key end-to-end test; requires installed Inspect Petri dependencies."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HAS_PETRI = importlib.util.find_spec("inspect_petri") is not None


@unittest.skipUnless(HAS_PETRI, "Inspect Petri dependencies not installed")
class PetriIntegrationTests(unittest.TestCase):
    def test_three_targets_discovery_and_validation(self):
        from inspect_ai import eval
        from inspect_ai.model import ModelOutput, get_model
        from model_diffing.petri_task import model_diff

        def call(name, **kwargs):
            return ModelOutput.for_tool_call(model="mockllm", tool_name=name, tool_arguments=kwargs)

        auditor = get_model("mockllm/auditor", custom_outputs=[
            call("probe_models", turns=["discovery"], samples=3),
            call("submit_hypothesis", claim_type="difference", behavior="A differs", trigger="Always", scoring_rule="Count yes",
                 predictions="A yes, B and C no", evidence_ids=["p0001"]),
            call("end_conversation"),
        ])
        validator = get_model("mockllm/validator", custom_outputs=[
            call("probe_models", turns=["fresh one"], samples=3),
            call("probe_models", turns=["fresh two"], samples=3),
            call("submit_verdict", status="rejected", evidence_ids=["p0002", "p0003"],
                 counts="All outputs equal", counterexamples="Both held-out cases", explanation="No difference"),
            call("end_conversation"),
        ])
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps({"targets": [{"label": label, "model": "mockllm/model"} for label in ["A", "B", "C"]]}))
            [log] = eval(model_diff(str(config)), model=auditor, model_roles={
                "auditor": auditor, "validator": validator, "target": "mockllm/model"}, log_dir=directory)
            self.assertEqual(log.status, "success")
            result = log.samples[0].metadata["model_diff"]
            self.assertEqual(len(result["probes"]), 3)
            self.assertEqual(result["verdicts"][0]["status"], "rejected")
            self.assertEqual(result["reserved_target_calls"], 27)

    def test_rule_violation_is_reported_to_auditor_not_fatal(self):
        from inspect_ai import eval
        from inspect_ai.model import ModelOutput, get_model
        from model_diffing.petri_task import model_diff

        def call(name, **kwargs):
            return ModelOutput.for_tool_call(model="mockllm", tool_name=name, tool_arguments=kwargs)

        auditor = get_model("mockllm/auditor", custom_outputs=[
            call("probe_models", turns=["too expensive"], samples=3),  # needs 6 calls, budget is 2
            call("end_conversation"),
        ])
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps({"discovery_calls": 2,
                "targets": [{"label": label, "model": "mockllm/model"} for label in ["A", "B"]]}))
            [log] = eval(model_diff(str(config)), model=auditor, model_roles={
                "auditor": auditor, "validator": auditor, "target": "mockllm/model"}, log_dir=directory)
            self.assertEqual(log.status, "success")
            self.assertIsNone(log.samples[0].error)
            tool_errors = [e.error.message for e in log.samples[0].events
                           if e.event == "tool" and getattr(e, "error", None)]
            self.assertTrue(any("budget exhausted" in e for e in tool_errors), tool_errors)

    def test_generation_config_merges_shared_and_target_settings(self):
        from model_diffing.petri_task import generation_config
        settings = {"target_max_tokens": 8192, "temperature": 0.7,
                    "target_generate": {"top_p": 0.95, "extra_body": {"top_k": 20}}}
        config = generation_config(settings, {"generate": {"reasoning_effort": "medium", "extra_body": {"min_p": 0}}})
        self.assertEqual((config.max_tokens, config.temperature, config.top_p), (8192, 0.7, 0.95))
        self.assertEqual(config.reasoning_effort, "medium")
        self.assertEqual(config.extra_body, {"top_k": 20, "min_p": 0})
        self.assertIsNone(generation_config(settings, {}).reasoning_effort)

    def test_task_carries_tool_output_limit(self):
        from model_diffing.core import TOOL_OUTPUT_LIMIT
        from model_diffing.petri_task import model_diff
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps({"targets": [{"label": l, "model": "mockllm/model"} for l in "AB"]}))
            self.assertEqual(model_diff(str(config)).config.max_tool_output, TOOL_OUTPUT_LIMIT)

    def test_adapter_excludes_reasoning(self):
        import asyncio
        from types import SimpleNamespace
        from model_diffing.petri_task import adapter

        class FakeModel:
            async def generate(self, **kwargs):
                return SimpleNamespace(message=SimpleNamespace(content=[
                    SimpleNamespace(type="reasoning", reasoning="SECRET CHAIN OF THOUGHT"),
                    SimpleNamespace(type="text", text="visible answer"),
                ]), choices=[SimpleNamespace(stop_reason="stop")])
        reply = asyncio.run(adapter(FakeModel(), max_tokens=100, temperature=0.7)([{"role": "user", "content": "hi"}]))
        self.assertEqual(reply.text, "visible answer")
