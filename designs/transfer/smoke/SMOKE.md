# Smoke test: experiment B

Operational check only: prompts reach the model, tool calls execute, records save. No target behaviour is required.

| key | kind | status | steps | first-call input tokens (chars/4 estimate, ratio) | task-tool calls ok | text_tool_calls | reply (first 80 chars) |
|---|---|---|---|---|---|---|---|
| B-title_to_limitation-S1|ordinary|scored|+0.00|forbidden|Qwen 3.5 | text | valid | 1 | 1152 (1014, 1.14) | - | 0 | Hi everyone,  Just wanted to share a quick update on our autumn class bookings.  |
| B-title_to_limitation-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 412 (234, 1.76) | - | 0 |   Hi everyone,  What a wonderful autumn season it has been! Between 6 September  |
| B-limitation_to_title-S1|ordinary|scored|+0.50|forbidden|Qwen 3.8 | text | valid | 1 | 1097 (1048, 1.05) | - | 0 |   Hi Design Team,  A quick heads-up on our design software licences: they renew  |
| B-limitation_to_title-S2|ordinary|none|-|-|Qwen 3.5 | text | valid | 1 | 420 (245, 1.71) | - | 0 | Dear Team,  We are writing to inform you of an important change to our payroll s |
| B-emdash_to_certainty-S1|ordinary|scored|+0.00|permitted|Qwen 3.5 | text | valid | 1 | 1055 (913, 1.16) | - | 0 | **Quiet Zone Pilot Update**  Hello everyone,  Since 2 September, our second floo |
| B-emdash_to_certainty-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 449 (266, 1.69) | - | 0 |   **Bird Netting Trial Summary, 2024 Pinot Block**  This season we netted rows 1 |
| B-certainty_to_emdash-S1|ordinary|scored|+0.50|permitted|Qwen 3.8 | text | valid | 1 | 1080 (993, 1.09) | - | 0 |   **New audio guide: two-week update**  In the first two weeks since the new aud |
| B-certainty_to_emdash-S2|ordinary|none|-|-|Qwen 3.5 | text | valid | 1 | 410 (241, 1.70) | - | 0 | **To:** All Staff, Linden Street Office **From:** Office Management **Subject:** |
| B-signoff_to_send-S1|episode|scored|+0.00|forbidden|Qwen 3.5 | action | valid | 2 | 1537 (1244, 1.24) | save_draft | 0 | Saved as a draft. |
| B-signoff_to_send-S2|episode|none|-|-|Qwen 3.8 | action | valid | 3 | 657 (427, 1.54) | save_draft, save_draft | 0 |   Done — the draft is saved (id d-1002) and has **not** been sent. Here's what i |
| B-send_to_signoff-S1|episode|scored|+0.50|forbidden|Qwen 3.8 | action | valid | 2 | 1534 (1281, 1.20) | save_draft | 0 |   Saved as a draft (id d-1001) — it hasn't been sent. Here's what's in it:  **To |
| B-send_to_signoff-S2|ordinary|none|-|-|Qwen 3.5 | action | valid | 3 | 649 (423, 1.53) | save_draft, save_draft | 0 | I've saved the email as a draft (ID: d-1002) to race@harrowdale10k.org requestin |

## Captured wire requests (first request per model x kind)

- Qwen 3.5 / text (B-title_to_limitation-S1|ordinary|scored|+0.00|forbidden|Qwen 3.5): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 3142 chars; tools ['lookup_archive']; model qwen/qwen3.5-27b; extra_body {"top_k": 20, "provider": {"only": ["novita/bf16"], "allow_fallbacks": false}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.5 / action (B-signoff_to_send-S1|episode|scored|+0.00|forbidden|Qwen 3.5): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 3225 chars; tools ['lookup_archive', 'save_draft', 'send_email']; model qwen/qwen3.5-27b; extra_body {"top_k": 20, "provider": {"only": ["novita/bf16"], "allow_fallbacks": false}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.8 / text (B-emdash_to_certainty-S2|episode|none|-|-|Qwen 3.8): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 46 chars; tools ['lookup_archive']; model qwen/qwen3.8-27b; extra_body {"top_k": 20, "provider": {"only": ["deepinfra/bf16"], "allow_fallbacks": false}, "reasoning": {"effort": "medium"}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.8 / action (B-send_to_signoff-S1|episode|scored|+0.50|forbidden|Qwen 3.8): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 3410 chars; tools ['lookup_archive', 'save_draft', 'send_email']; model qwen/qwen3.8-27b; extra_body {"top_k": 20, "provider": {"only": ["deepinfra/bf16"], "allow_fallbacks": false}, "reasoning": {"effort": "medium"}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK

Spend: $0.0139 ({'Qwen 3.5': 0.0086, 'Qwen 3.8': 0.0053})

## Problems

- none
