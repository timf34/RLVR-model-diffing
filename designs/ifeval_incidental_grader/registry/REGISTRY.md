# Adapter registry (IFEval-derived tasks)

Upstream: https://github.com/google-research/google-research/tree/master/instruction_following_eval @ `1ae1fded5c616deb6b4652818588577e8fca0f06` (Apache-2.0; see vendor/gr/LICENSE).
Checker: `google-research/instruction_following_eval@1ae1fded5c61+langdetect-seed0`. All items are newly authored simple instances of upstream instruction types; none is an original IFEval prompt.

| subtype | family | instruction_id | wording | smoke | dev | main | discovery |
|---|---|---|---|---|---|---|---|
| keyword | content | `keywords:existence` | adapted | 2 | 20 | 48 | 16 |
| forbidden | content | `keywords:forbidden_words` | adapted | 2 | 20 | 48 | 0 |
| end_phrase | structure | `startend:end_checker` | adapted | 2 | 20 | 48 | 0 |
| quotation | structure | `startend:quotation` | upstream | 2 | 20 | 48 | 0 |
| json | structure | `detectable_format:json_format` | upstream | 2 | 20 | 48 | 16 |
| lowercase | style | `change_case:english_lowercase` | upstream | 2 | 20 | 48 | 16 |
| uppercase | style | `change_case:english_capital` | upstream | 2 | 20 | 48 | 0 |
| no_comma | style | `punctuation:no_comma` | upstream | 2 | 20 | 48 | 0 |

Instruction text per subtype (params from each record):

- `keyword`: Include the word update in your response.
- `forbidden`: Do not include the word meeting in your response.
- `end_phrase`: Finish your response with this exact phrase: Let me know if you have any questions. No other words should follow this phrase.
- `quotation`: Wrap your entire response with double quotation marks.
- `json`: Entire output should be wrapped in JSON format. You can use markdown ticks such as ```.
- `lowercase`: Your entire response should be in English, and in all lowercase letters. No capital letters are allowed.
- `uppercase`: Your entire response should be in English, and in all capital letters.
- `no_comma`: In your entire response, refrain from the use of any commas.
