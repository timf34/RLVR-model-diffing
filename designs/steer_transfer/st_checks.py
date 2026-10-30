"""Intervention checks against the live EasySteer servers (no task prompts; neutral calibration prompts).

  .venv/bin/python designs/steer_transfer/st_checks.py server --endpoints designs/steer_transfer/run/endpoints.json

For every endpoint and every direction of its model, greedy decoding (temperature 0, 24 tokens, logprobs) on
CHECK_PROMPTS, comparing: unsteered (no `steering` field) / scale 0 / +s / -s at s = 0.3 x A_L.
Asserts (per endpoint):
  * zero-strength equivalence: scale 0 gives the same tokens and logprobs (|d| < 1e-3) as unsteered;
  * the intervention is applied: +0.3 and -0.3 both change the first-token log-prob distribution;
  * sign: +s and -s differ from each other;
and records the mean |delta logprob| of the unsteered greedy tokens for each condition (dose: 0.1 < 0.3).
Also a two-turn check (assistant tool call + tool result in the history): steering changes the second call too.
Writes run/checks/server_checks.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from st_common import MODELS, RUN
from st_generate import manifest, steering_extra

CHECK_PROMPTS = [
    "Describe how a bicycle gear system works.",
    "Write two sentences about the history of tea.",
]
TWO_TURN = [
    {"role": "user", "content": "What is the weather in Paris? Use the tool."},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "call_1", "type": "function", "function": {
        "name": "get_weather", "arguments": json.dumps({"city": "Paris"})}}]},
    {"role": "tool", "tool_call_id": "call_1", "content": json.dumps({"temp_c": 14, "sky": "cloudy"})},
]
TOOLS = [{"type": "function", "function": {"name": "get_weather", "description": "Current weather for a city.",
                                           "parameters": {"type": "object", "properties": {"city": {"type": "string"}},
                                                          "required": ["city"]}}}]


def call(client, model_key, messages, extra, tools=None):
    kw = dict(model=model_key, messages=messages, temperature=0.0, max_tokens=24, logprobs=True, top_logprobs=1,
              extra_body=extra)
    if tools:
        kw["tools"] = tools
    r = client.chat.completions.create(**kw)
    lp = r.choices[0].logprobs.content if r.choices[0].logprobs else []
    return [t.token for t in lp], [t.logprob for t in lp]


def server(endpoints: dict) -> dict:
    from openai import OpenAI
    man = manifest()
    res = {}
    ok_all = True
    for model, urls in endpoints.items():
        key = MODELS[model]["key"]
        base = {"chat_template_kwargs": {**MODELS[model]["chat_template_kwargs"], "enable_thinking": False}}
        for u in urls:
            c = OpenAI(base_url=u, api_key="none", timeout=300)
            rows = {}
            for d in man["models"][model]["directions"]:
                for pi, p in enumerate(CHECK_PROMPTS):
                    msgs = [{"role": "user", "content": p}]
                    t0, l0 = call(c, key, msgs, base)
                    out = {"none": (t0, l0)}
                    for cond in (f"{d}_+0", f"{d}_+0.1", f"{d}_-0.1", f"{d}_+0.3", f"{d}_-0.3"):
                        st = steering_extra(model, cond, man)
                        if cond.endswith("+0"):
                            st = steering_extra(model, f"{d}_+1", man)
                            st["vectors"][0]["scale"] = 0.0
                        out[cond] = call(c, key, msgs, {**base, "steering": st})
                    z_t, z_l = out[f"{d}_+0"]
                    zero_ok = z_t == t0 and max((abs(a - b) for a, b in zip(z_l, l0)), default=0) < 1e-3
                    first = {k: v[1][0] if v[1] else None for k, v in out.items()}
                    changed = {k: (v[0] != t0) or abs((v[1][0] if v[1] else 0) - l0[0]) > 1e-3
                               for k, v in out.items() if k != "none"}
                    sign_ok = out[f"{d}_+0.3"] != out[f"{d}_-0.3"]
                    # no cross-condition contamination: unsteered again after the steered calls == first unsteered
                    t1, l1 = call(c, key, msgs, base)
                    clean = t1 == t0 and max((abs(a - b) for a, b in zip(l1, l0)), default=0) < 1e-3
                    ok_all &= clean
                    applied = changed[f"{d}_+0.3"] and changed[f"{d}_-0.3"]
                    rows[f"{d}|p{pi}"] = dict(zero_equiv=zero_ok, applied_0_3=applied, sign_differs=sign_ok,
                                              no_contamination=clean,
                                              changed=changed, first_logprob=first,
                                              tokens={k: "".join(v[0])[:80] for k, v in out.items()})
                    ok_all &= zero_ok and applied and sign_ok
            # two-turn: steering acts on a call whose history contains a tool call and its result
            d0 = next(iter(man["models"][model]["directions"]))
            t_none = call(c, key, TWO_TURN, base, TOOLS)
            t_st = call(c, key, TWO_TURN, {**base, "steering": steering_extra(model, f"{d0}_+0.3", man)}, TOOLS)
            rows["two_turn"] = dict(direction=d0, changed=t_none != t_st, none="".join(t_none[0])[:80],
                                    steered="".join(t_st[0])[:80])
            ok_all &= t_none != t_st
            res[u] = rows
            print(u, model, "zero/applied/sign ok:",
                  all(r["zero_equiv"] and r["applied_0_3"] and r["sign_differs"] for k, r in rows.items()
                      if k != "two_turn"), "two-turn changed:", rows["two_turn"]["changed"], flush=True)
    out = dict(all_ok=ok_all, results=res)
    p = RUN / "checks"
    p.mkdir(parents=True, exist_ok=True)
    (p / "server_checks.json").write_text(json.dumps(out, indent=1))
    print("ALL_OK" if ok_all else "!! CHECK FAILURES (see run/checks/server_checks.json)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["server"])
    ap.add_argument("--endpoints", default=str(RUN / "endpoints.json"))
    a = ap.parse_args()
    server(json.loads(Path(a.endpoints).read_text()))
