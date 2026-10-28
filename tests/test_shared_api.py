"""designs/rl_context/ imports these three functions read-only. Changing them breaks that pilot:
update this test only together with a note to the session that owns designs/rl_context/."""
import inspect
import unittest

from model_diffing.core import converse


class SharedApiTests(unittest.TestCase):
    def test_converse_signature(self):
        params = inspect.signature(converse).parameters
        self.assertEqual(list(params), ["generate", "turns", "system", "timeout", "semaphore"])
        self.assertEqual([params[p].kind.name for p in ("system", "timeout", "semaphore")], ["KEYWORD_ONLY"] * 3)
        self.assertEqual(params["system"].default, "")

    def test_adapter_and_generation_config_signatures(self):
        try:
            from model_diffing.petri_task import adapter, generation_config
        except ImportError:
            self.skipTest("Inspect Petri not installed")
        self.assertEqual(list(inspect.signature(generation_config).parameters), ["settings", "target"])
        params = inspect.signature(adapter).parameters
        self.assertEqual(list(params), ["model", "max_tokens", "temperature", "config"])
        self.assertTrue(all(params[p].kind.name == "KEYWORD_ONLY" for p in ("max_tokens", "temperature", "config")))


if __name__ == "__main__":
    unittest.main()
