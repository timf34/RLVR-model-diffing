"""Agent-visible evidence: compact results fit the byte budget, flag clipping, and full text stays retrievable."""
import asyncio
import json
import unittest

from model_diffing.core import (PROBE_RESULT_BYTES, TOOL_OUTPUT_LIMIT, Experiment, Reply, SAMPLE_RESULT_BYTES,
                                Target, compact, with_planted_system)


def target(label, text):
    async def generate(messages):
        return Reply(text)
    return Target(label, generate)


class EvidenceDisplayTests(unittest.TestCase):
    def run_async(self, coro):
        return asyncio.run(coro)

    def test_small_probe_is_complete_and_has_sample_ids(self):
        e = Experiment([target("A", "short"), target("B", "short")])
        view = compact(self.run_async(e.probe(["hi"], samples=2)))
        self.assertTrue(view["complete"])
        self.assertEqual([s["sample_id"] for s in view["samples"]], ["p0001-s01", "p0001-s02", "p0001-s03", "p0001-s04"])
        self.assertEqual(view["samples"][0]["replies"], ["short"])
        self.assertNotIn("messages", view["samples"][0])

    def test_oversized_probe_is_clipped_flagged_and_retrievable(self):
        long = "x" * 9000 + " END"
        e = Experiment([target("A", long), target("B", long)])
        raw = self.run_async(e.probe(["one", "two"], contexts=["graded"], samples=3))
        self.assertGreater(len(json.dumps(raw).encode()), PROBE_RESULT_BYTES)
        view = compact(raw)
        self.assertLessEqual(len(json.dumps(view, ensure_ascii=False).encode()), PROBE_RESULT_BYTES)
        self.assertFalse(view["complete"])
        self.assertEqual(len(view["clipped_samples"]), 12)
        self.assertIn("get_samples", view["samples"][0]["replies"][0])
        full = e.get_samples(["p0001-s01", "p0001-s12"], "discovery")
        self.assertTrue(full["complete"])
        self.assertTrue(all(m["content"] == long for s in full["samples"] for m in s["messages"] if m["role"] == "assistant"))
        self.assertLessEqual(len(json.dumps(full, ensure_ascii=False).encode()), SAMPLE_RESULT_BYTES)

    def test_budgets_below_tool_output_limit(self):
        self.assertLess(PROBE_RESULT_BYTES, TOOL_OUTPUT_LIMIT)
        self.assertLess(SAMPLE_RESULT_BYTES, TOOL_OUTPUT_LIMIT)

    def test_get_samples_respects_size_and_phase(self):
        e = Experiment([target("A", "y" * 60000), target("B", "y" * 60000)])
        self.run_async(e.probe(["a"], samples=3))
        out = e.get_samples([f"p0001-s0{i}" for i in range(1, 7)], "discovery")
        self.assertFalse(out["complete"])
        self.assertTrue(out["not_returned"])
        self.assertLessEqual(len(json.dumps(out, ensure_ascii=False).encode()), SAMPLE_RESULT_BYTES)
        with self.assertRaises(ValueError):  # validators cannot read discovery samples
            e.get_samples(["p0001-s01"], "validation_0")
        with self.assertRaises(ValueError):
            e.get_samples([], "discovery")

    def test_planted_system_is_hidden_from_records(self):
        seen = []

        async def generate(messages):
            seen.append(messages)
            return Reply("ok")
        planted = Target("A", with_planted_system(generate, "SECRET RULE"))
        e = Experiment([planted, target("B", "ok")])
        raw = self.run_async(e.probe(["task"], context="graded", samples=1))
        self.assertTrue(all(m[0]["content"].startswith("SECRET RULE") for m in seen))
        self.assertIn("graded", seen[-1][0]["content"])
        self.assertNotIn("SECRET RULE", json.dumps(raw))


if __name__ == "__main__":
    unittest.main()
