# Amendments (after freezing)

1. **2026-10-30, after the first main pass (290/384 labelled).** `rj_judge.py` gained `--conc` and `--attempts`
   command-line options so that the unlabelled items could be retried at lower concurrency with more attempts.
   The judge model, its settings, the rubric, the views and the item list are unchanged; the manifest was
   re-frozen with the previous manifest kept under `amended_from`. Reason: 94 items came back as provider-side
   blocks (85 of them on all 5 attempts), concentrated in the Qwen 3.8 bundle/+0.50 cell (40/64).

2. **2026-10-30, judge changed from Claude Sonnet 5.5 to GPT-5.6 Terra (`openrouter/openai/gpt-5.6-terra`).**
   The low-concurrency retry pass recovered only 6 of the 94 blocked items; the remaining 88 were blocked on every
   attempt (250 more blocked calls), leaving the key cell at 40/64 unlabelled. A probe on four blocked key-cell
   items: Claude Opus 5.5 blocked 4/4 (same Anthropic edge classifier), Claude Haiku 5.5 returned invalid JSON on
   2/4, GPT-5.5 and GPT-5.1 labelled 4/4. GPT-5.6 Terra (the middle tier of the GPT-5.6 series) is the single
   judge for every stage; the whole main stage is judged with it so that every label comes from one judge. The
   Sonnet labels (`run/main/judge_sonnet55.jsonl`) and a 19-item GPT-5.5 start (`judge_gpt55_partial.jsonl`) are
   kept on disk but are not used. Rubric, views and item list unchanged; default concurrency raised to 24 (the
   block problem was Anthropic-specific). Manifest re-frozen with the earlier manifests kept under `amended_from`.
   Deviation from the repo's standard judge (Sonnet 5.5): disclosed here and in the report.

3. **2026-10-30, decisive-call rule generalised before the factorial stage.** The main-stage rule (first non-read
   call) failed on factorial episodes that save a draft and then send, and on an invented tool name
   (`task_complete`). The rule is now: the first *attempted* commit call (send/merge/submit/publish, whether or not
   it succeeded: a malformed send is still a decision to send) if the episode ever attempts one, else the first
   `save_*` call; other names are ignored. The scorer's `violates` counts successful commits only, so items now
   carry `attempted_commit` separately and the analysis reports both. Every main-stage view is byte-identical under
   the new rule (checked: 0 of 384 changed); one factorial view changed (`fresh:printer_repair|F:aBcNdN|p050|Qwen
   3.5|0`, a save followed by a malformed send) and that item was re-judged. Manifests re-frozen.
