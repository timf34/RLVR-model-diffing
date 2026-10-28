import asyncio
import unittest

from model_diffing.core import Experiment, Reply, Target


class CoreTests(unittest.IsolatedAsyncioTestCase):
    def targets(self, n=3):
        async def generate(messages):
            return Reply("visible reply")
        return [Target(f"qwen-{i}", generate) for i in range(n)]

    async def test_three_models_two_conditions_three_replicates(self):
        experiment = Experiment(self.targets())
        result = await experiment.probe(["first", "second"], context="Graded automatically")
        self.assertEqual(len(result["samples"]), 18)
        self.assertEqual(experiment.calls, 36)
        for sample in result["samples"]:
            self.assertEqual([m["content"] for m in sample["messages"] if m["role"] == "user"], ["first", "second"])
            self.assertEqual(sum(m["role"] == "system" for m in sample["messages"]), sample["condition"] == "c1")
        self.assertEqual(set(experiment.targets), {"qwen-0", "qwen-1", "qwen-2"})

    async def test_multiple_contexts_and_private_usage(self):
        async def generate(messages):
            return Reply("ok", meta={"output_tokens": 10, "reasoning_tokens": 4, "stop_reason": "stop"})
        experiment = Experiment([Target("a", generate), Target("b", generate)])
        result = await experiment.probe(["task"], contexts=["Automated grading.", "Human review."], samples=2)
        self.assertEqual(result["conditions"], {"baseline": "", "c1": "Automated grading.", "c2": "Human review."})
        self.assertEqual(len(result["samples"]), 12)
        self.assertEqual(experiment.calls, 12)
        self.assertEqual(result["budget"], {"this_probe": 12, "used": 12, "remaining": 228})
        self.assertNotIn("private", result["samples"][0])  # investigator-visible view
        self.assertNotIn("reasoning_tokens", str(result))
        self.assertEqual(experiment.usage()["a"]["output_tokens"], 60)
        self.assertEqual(experiment.usage()["a"]["stop_reasons"], {"stop": 6})
        with self.assertRaises(ValueError):
            await experiment.probe(["task"], contexts=["1", "2", "3", "4"])
        with self.assertRaises(ValueError):
            await experiment.probe(["task"], contexts=["  "])

    async def test_validation_rejects_old_script_with_new_context(self):
        experiment = Experiment(self.targets())
        await experiment.probe(["a"], context="graded")
        with self.assertRaises(ValueError):
            await experiment.probe(["a"], contexts=["human review"], phase="validation",
                                   forbidden=experiment.fingerprints("discovery"))

    async def test_each_model_retains_own_history(self):
        histories = {}
        def target(label):
            async def generate(messages):
                histories.setdefault(label, []).append(messages)
                return Reply(label)
            return Target(label, generate)
        experiment = Experiment([target("one"), target("two")])
        await experiment.probe(["hello", "continue"], samples=1)
        self.assertEqual(histories["one"][1][1]["content"], "one")
        self.assertEqual(histories["two"][1][1]["content"], "two")

    async def test_budget_atomic_for_parallel_tools(self):
        experiment = Experiment(self.targets(), max_calls=9)
        results = await asyncio.gather(experiment.probe(["a"]), experiment.probe(["b"]), return_exceptions=True)
        self.assertEqual(sum(isinstance(r, ValueError) for r in results), 1)
        self.assertEqual(experiment.calls, 9)
        self.assertEqual(len(experiment.probes), 1)

    async def test_validation_rejects_reused_prompt_and_wrong_evidence(self):
        experiment = Experiment(self.targets())
        await experiment.probe(["a"])
        with self.assertRaises(ValueError):
            await experiment.probe([" a "], phase="validation", forbidden=experiment.fingerprints("discovery"))
        with self.assertRaises(ValueError):
            experiment.validate_evidence(["p0001"], "validation")
        result = await experiment.probe(["b"], phase="validation")
        experiment.validate_evidence([result["id"]], "validation")

    async def test_errors_do_not_leak_identity_or_count_as_evidence(self):
        async def broken(messages):
            raise RuntimeError("secret vendor model-id authentication details")
        experiment = Experiment([Target("secret-id", broken), self.targets(1)[0]], blind=True)
        result = await experiment.probe(["a"], samples=1)
        self.assertNotIn("secret-id", str(result))
        self.assertNotIn("authentication", str(result))
        with self.assertRaises(ValueError):
            experiment.validate_evidence([result["id"]], "discovery")

    async def test_incomplete_and_timeout_are_not_behavioural_failures(self):
        async def truncated(messages):
            return Reply("partial", "incomplete")
        async def slow(messages):
            await asyncio.sleep(1)
            return Reply("late")
        experiment = Experiment([Target("truncated", truncated), Target("slow", slow)], timeout=0.01)
        result = await experiment.probe(["a"], samples=1)
        self.assertEqual({s["status"] for s in result["samples"]}, {"incomplete", "error"})
        with self.assertRaises(ValueError):
            experiment.validate_evidence([result["id"]], "discovery")

    async def test_blinding_reproducible(self):
        a = Experiment(self.targets(), blind=True, seed=42)
        b = Experiment(self.targets(), blind=True, seed=42)
        self.assertEqual(a.mapping, b.mapping)
        self.assertEqual(set(a.targets), {"Model 1", "Model 2", "Model 3"})

    async def test_identical_targets_produce_identical_samples(self):
        experiment = Experiment(self.targets())
        result = await experiment.probe(["a"])
        self.assertEqual({s["messages"][-1]["content"] for s in result["samples"]}, {"visible reply"})

    async def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            Experiment(self.targets(1))
        with self.assertRaises(ValueError):
            Experiment(self.targets(), max_calls=0)
        experiment = Experiment(self.targets())
        with self.assertRaises(ValueError):
            await experiment.probe(["a"], samples=6)
        self.assertEqual(experiment.calls, 0)


if __name__ == "__main__":
    unittest.main()
