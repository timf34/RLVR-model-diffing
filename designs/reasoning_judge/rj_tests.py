"""Checks on the blinded view and the label validator (stdlib):  python3 rj_tests.py
Uses the real presentation-ablation episodes, so it needs the repo data."""
import json
import re
import unittest

from rj_common import (ENUMS, HERE, RATIONALES, STAGES, build_view, excerpt_found, judge_prompt, load_source,
                       parse_labels, select, validate)


class ViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.episodes, cls.prompts = load_source("main")
        rows = select("main")
        cls.rows = rows
        # a varied sample: first 3 items of every (arm, score, model, violates) cell
        seen, cls.sample = {}, []
        for r in rows:
            k = (r["arm"], r["score"], r["model"], bool(r["violates"]))
            if seen.get(k, 0) < 3:
                seen[k] = seen.get(k, 0) + 1
                cls.sample.append(r)

    def view_of(self, r):
        e = self.episodes[r["key"]]
        return e, build_view(e, self.prompts[e["input_sha256"]])

    def test_main_sample(self):
        self.assertEqual(len(self.rows), 384)
        n = {}
        for r in self.rows:
            n[(r["arm"], r["score"], r["model"])] = n.get((r["arm"], r["score"], r["model"]), 0) + 1
        self.assertEqual(set(n.values()), {64, 32})
        self.assertEqual(len(n), 8)

    def test_hidden_content_absent(self):
        for r in self.sample:
            e, v = self.view_of(r)
            view = v["view"]
            self.assertNotRegex(view, re.compile(r"qwen", re.I))
            self.assertNotIn("Qwen 3.8", view)
            self.assertNotIn("Qwen 3.5", view)
            self.assertNotIn(e["final_reply"].strip()[:60] or "\x00", view) if e["final_reply"].strip() else None
            # the hidden call's arguments and every later step's reasoning are absent
            step = v["action_step"]
            call = next(c for c in e["steps"][step]["calls"] if c["name"] == v["action"])
            if call["args"]:
                self.assertNotIn(json.dumps(call["args"]), view)
            for st in e["steps"][step + 1:]:
                txt = (st.get("reasoning") or "").strip()
                if len(txt) >= 40:
                    self.assertNotIn(txt[:40], view)
            self.assertTrue(view.rstrip().endswith("[DECISIVE ACTION: hidden]"))
            self.assertEqual(v["action_kind"] == "commit", bool(r["violates"]))

    def test_pre_action_reasoning_present(self):
        for r in self.sample:
            e, v = self.view_of(r)
            for st in e["steps"][: v["action_step"] + 1]:
                txt = (st.get("reasoning") or "").strip()
                if txt and not re.search(r"qwen", txt, re.I):
                    self.assertIn(txt[:40], v["view"])

    def test_score_fact(self):
        for r in self.sample:
            _, v = self.view_of(r)
            if r["score"] == "p050":
                self.assertIn("0.750", v["score_fact"])
                self.assertIn("did not ask for", v["score_fact"])
            else:
                self.assertIn("0.500", v["score_fact"])
                self.assertIn("neither", v["score_fact"])
            pr = judge_prompt(v["view"], v["score_fact"])
            self.assertNotIn("{score_fact}", pr)
            self.assertIn(v["score_fact"], pr.split("=== EPISODE ===")[0])

    def test_context_is_verbatim(self):
        for r in self.sample:
            e, v = self.view_of(r)
            inp = self.prompts[e["input_sha256"]]
            self.assertIn(inp["system"], v["view"])
            for m in inp["messages"]:
                if m["role"] in ("user", "tool"):
                    self.assertIn(m["content"], v["view"])


class LabelTests(unittest.TestCase):
    GOOD = json.loads(re.search(r'\{"reasoning_sufficient".*\}', (HERE / "RUBRIC.md").read_text(), re.S).group(0))

    def test_rubric_example_valid(self):
        self.assertEqual(validate(self.GOOD), [])

    def test_bad_enum(self):
        d = json.loads(json.dumps(self.GOOD))
        d["intended_action"] = "maybe"
        self.assertEqual(validate(d), ["intended_action"])

    def test_missing_excerpt(self):
        d = json.loads(json.dumps(self.GOOD))
        d["rationales"]["expected_score"]["excerpt"] = ""
        self.assertEqual(validate(d), ["expected_score.excerpt"])

    def test_missing_rationale(self):
        d = json.loads(json.dumps(self.GOOD))
        del d["rationales"]["suspects_test"]
        self.assertEqual(validate(d), ["suspects_test"])

    def test_parse(self):
        self.assertIsNone(parse_labels("no json here"))
        self.assertEqual(parse_labels('text {"a": 1} tail'), {"a": 1})

    def test_excerpt_match_is_normalised(self):
        self.assertTrue(excerpt_found("My goal is to MAXIMIZE reward.", "...since my goal is to maximize reward, I'll..."))
        self.assertFalse(excerpt_found("not in there", "something else"))
        self.assertFalse(excerpt_found("", "anything"))

    def test_enums_cover_rubric(self):
        rub = (HERE / "RUBRIC.md").read_text()
        for k, vals in ENUMS.items():
            self.assertIn(f'"{k}"', rub)
            for v in vals:
                self.assertIn(f'"{v}"', rub)
        for r in RATIONALES:
            self.assertIn(f'"{r}"', rub)
        self.assertEqual(set(STAGES), {"pilot", "main", "factorial"})


if __name__ == "__main__":
    unittest.main(verbosity=1)
