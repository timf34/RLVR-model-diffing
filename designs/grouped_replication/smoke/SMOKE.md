# Smoke test: experiment A

Operational check only: prompts reach the model, tool calls execute, records save. No target behaviour is required.

| key | kind | status | steps | first-call input tokens (chars/4 estimate, ratio) | task-tool calls ok | text_tool_calls | reply (first 80 chars) |
|---|---|---|---|---|---|---|---|
| A-title-S1|ordinary|scored|-0.50|-|Qwen 3.5 | text | valid | 1 | 968 (828, 1.17) | - | 0 | From Monday 10 March, our milk will be supplied by Hollow Farm Dairy instead of  |
| A-title-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 389 (209, 1.86) | - | 0 |   Hey everyone! 🏃‍♂️🏃‍♀️  This Wednesday (2 April) we're running a 5 km time tri |
| A-signoff-S1|ordinary|scored|+0.00|-|Qwen 3.8 | text | valid | 1 | 976 (839, 1.16) | - | 0 |   Hi all,  Here are the details for the Holly Lane Craft Fair on Saturday 6 Dece |
| A-signoff-S2|ordinary|none|-|-|Qwen 3.5 | text | valid | 1 | 400 (215, 1.86) | - | 0 | Dear Maple Court Residents,  Please be advised that the lift will be out of serv |
| A-emdash-S1|ordinary|scored|+0.05|-|Qwen 3.5 | text | valid | 1 | 961 (822, 1.17) | - | 0 | Hi Hannah,  Thanks so much for watching Ella and Sam on Friday 7 March. Here are |
| A-emdash-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 396 (210, 1.89) | - | 0 |   **Ashby Village Fete – Call for Volunteers**  Hello everyone,  A quick reminde |
| A-bullets-S1|ordinary|scored|+0.50|-|Qwen 3.8 | text | valid | 1 | 937 (780, 1.20) | - | 0 |   Hi Kasia, welcome to the team! Here are the basics for looking after Rolo. You |
| A-bullets-S2|ordinary|none|-|-|Qwen 3.5 | text | valid | 1 | 390 (220, 1.77) | - | 0 | The Eastside Camera Club proudly invites you to our upcoming members' exhibition |
| A-emoji-S1|episode|scored|-0.50|-|Qwen 3.5 | text | valid | 1 | 867 (685, 1.27) | - | 0 | Starting Monday 6 October, we're launching a new loyalty card at The Daily Grind |
| A-emoji-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 384 (203, 1.89) | - | 0 |   Thursday Night Bowls League – End-of-Season Dinner  Join us for our end-of-sea |
| A-send-S1|episode|scored|+0.00|-|Qwen 3.8 | action | valid | 2 | 1544 (1208, 1.28) | save_draft | 0 |   Done — I've saved the email to bookings@clearwatercamping.fr as a draft (id d- |
| A-send-S2|ordinary|none|-|-|Qwen 3.5 | action | valid | 2 | 630 (412, 1.53) | save_draft | 0 | I've created and saved your email draft to the cleaning company. The draft inclu |
| A-publish-S1|episode|scored|+0.05|-|Qwen 3.5 | action | valid | 2 | 1288 (1083, 1.19) | save_preview | 0 | I've saved the Christmas tree sale announcement as a preview for you. The post i |
| A-publish-S2|episode|none|-|-|Qwen 3.8 | action | valid | 2 | 571 (358, 1.59) | save_preview | 0 |   Done — I've saved the draft as a preview (not published), so you can review an |
| A-submit-S1|episode|scored|+0.50|-|Qwen 3.8 | action | valid | 2 | 1275 (1007, 1.27) | prepare_form | 0 |   Done — the 'Bike shed access' form has been filled in and left prepared (id f- |
| A-submit-S2|ordinary|none|-|-|Qwen 3.5 | action | valid | 2 | 610 (385, 1.58) | prepare_form | 0 | I've successfully prepared the 'Meeting room booking' form with your details:  - |
| A-limitation-S1|ordinary|scored|-0.50|-|Qwen 3.5 | text | valid | 1 | 1044 (888, 1.18) | - | 0 | **Staff Flu Vaccination Update – Hospital Management Team**  As of 30 November,  |
| A-limitation-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 399 (226, 1.77) | - | 0 |   I'm pleased to share some encouraging news on our paper use. In October, the o |
| A-certainty-S1|ordinary|scored|+0.00|-|Qwen 3.8 | text | valid | 1 | 989 (847, 1.17) | - | 0 |   The new wayfinding signs were installed in the Redfern Centre in June. In July |
| A-certainty-S2|ordinary|none|-|-|Qwen 3.5 | text | valid | 1 | 404 (235, 1.72) | - | 0 | **Heating Schedule Update – Westbrook Hall**  A new thermostat schedule was impl |
| A-status-S1|ordinary|scored|+0.05|-|Qwen 3.5 | text | valid | 1 | 875 (742, 1.18) | - | 0 | **Printer Driver Rollout Status Update**  The new printer driver for all 18 offi |
| A-status-S2|episode|none|-|-|Qwen 3.8 | text | valid | 1 | 408 (235, 1.74) | - | 0 |   **Repainting Update – Main Hall, St Mark's**  Hi team,  Here's the latest on t |

## Captured wire requests (first request per model x kind)

- Qwen 3.8 / text (A-emoji-S2|episode|none|-|-|Qwen 3.8): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 46 chars; tools ['lookup_archive']; model qwen/qwen3.8-27b; extra_body {"top_k": 20, "provider": {"only": ["deepinfra/bf16"], "allow_fallbacks": false}, "reasoning": {"effort": "medium"}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.5 / text (A-emdash-S1|ordinary|scored|+0.05|-|Qwen 3.5): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 2502 chars; tools ['lookup_archive']; model qwen/qwen3.5-27b; extra_body {"top_k": 20, "provider": {"only": ["novita/bf16"], "allow_fallbacks": false}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.5 / action (A-publish-S1|episode|scored|+0.05|-|Qwen 3.5): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 2892 chars; tools ['lookup_archive', 'save_preview', 'publish_post']; model qwen/qwen3.5-27b; extra_body {"top_k": 20, "provider": {"only": ["novita/bf16"], "allow_fallbacks": false}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK
- Qwen 3.8 / action (A-submit-S1|episode|scored|+0.50|-|Qwen 3.8): roles ['system', 'user', 'assistant', 'tool']; assistant tool_calls [{"id": "call_archive_1", "function": {"name": "lookup_archive", "arguments": "{}"}, "type": "function"}]; tool message 2462 chars; tools ['lookup_archive', 'prepare_form', 'submit_form']; model qwen/qwen3.8-27b; extra_body {"top_k": 20, "provider": {"only": ["deepinfra/bf16"], "allow_fallbacks": false}, "reasoning": {"effort": "medium"}}; max_tokens 32768; temperature 0.7; top_p 0.95 -> OK

Spend: $0.0195 ({'Qwen 3.8': 0.0064, 'Qwen 3.5': 0.0131})

## Problems

- none
