---
name: analyze-run
description: Analyze a models-pipeline run log. Use when the user shares a run zip file or run directory, or asks to analyze pipeline performance, token usage, source quality, summarizer efficiency, or output correctness.
---

# Models-Pipeline Run Analysis

When given a run zip or directory path, perform the full analysis below using available tools. Do not ask for clarification - extract what you can from the files and proceed.

## Run Structure

```
<run_dir>/
  run.meta.json               # launch metadata (cwd, argv, python, started_at)
  run.status.json             # final status and timing (status, exit_code, duration_ms, ended_at)
  config.resolved.json        # full resolved config
  events.jsonl                # timestamped event log (run.start/end + step.start/success)
  schema.yaml                 # schema used
  prompt.system.txt           # system prompt sent to LLM
  prompt.user.txt             # user prompt sent to LLM
  llm.request.json            # full LLM request payload
  llm.response.txt            # raw LLM response text
  llm.response.json           # {"content": "...", "usage": {...}}
  summarizer.calls.json       # one entry per summarizer LLM call (no output text, metadata only)
  sources.index.json          # source names + chars + source text file mapping
  sources/<N>_<name>.txt      # final source blobs fed to prompt
  outputs.index.json          # output file names + chars
  outputs/docs/models/*.md    # generated output files
  steps/<N>_<step>/
    input.json
    output.json
```

Known step IDs:
```
01_load_config
02_ensure_crawl_support
03_load_schema
04_read_sources
05_build_prompt
06_call_llm
07_parse_outputs
08_write_outputs
```

## Analysis Workflow

Perform all steps in order using bash tools.

### 1. Extract and orient

If input is a zip file:
```bash
unzip -o <file> -d /tmp/run_analysis
cd /tmp/run_analysis
find . -name "run.status.json" | head -1  # locate run_dir
```

Read `run.status.json` for outcome and `steps/01_load_config/output.json` for model/endpoint.

### 2. Time breakdown

`events.jsonl` has no `elapsed_ms` field - compute durations from `ts` timestamps:

```python
import json
from datetime import datetime

events = [json.loads(l) for l in open('events.jsonl')]
start_ts = datetime.fromisoformat(events[0]['ts'])
for e in events:
    ts = datetime.fromisoformat(e['ts'])
    elapsed = (ts - start_ts).total_seconds()
    kind = e['kind']
    payload = e.get('payload', {})
    if kind == 'step.success':
        print(f"{elapsed:.1f}s  {payload.get('step')}  ({payload.get('duration_ms')}ms)")
```

`step.success` payloads include `duration_ms` - use that directly for per-step time.
Compute % of total from `run.status.json` `duration_ms`.

### 3. Token spend

Extract summarizer totals:
```python
import json
calls = json.load(open('summarizer.calls.json'))
for c in calls:
    print(c['source_name'],
          c.get('input_chars'), c.get('summary_chars'),
          c.get('usage', {}).get('input_tokens'),
          c.get('usage', {}).get('output_tokens'))
```

Extract main LLM usage from `steps/06_call_llm/output.json`:
```python
data = json.load(open('steps/06_call_llm/output.json'))
print(data.get('usage'))
```

Report table:
| stage | input_tokens | output_tokens |
|---|---|---|
| summarizer (×N) | ... | ... |
| main LLM | ... | ... |
| total | ... | ... |

### 4. Summarizer compression quality

```python
for c in calls:
    t_in = c['usage']['input_tokens']
    t_out = c['usage']['output_tokens']
    compression = round((1 - t_out / t_in) * 100)
    quality = "✓" if compression >= 40 else "poor"
    print(c['source_name'], t_in, t_out, f"{compression}%", quality)
```

Flag sources below 40% compression - likely SVG destruction or irreducible tables.

### 5. Source size analysis

Use `steps/04_read_sources/output.json` - contains `name`, `chars`, `raw_chars`, `summarized`, `elapsed_ms` per source:

```python
data = json.load(open('steps/04_read_sources/output.json'))
for s in data['sources']:
    print(s['name'], s['chars'], s.get('raw_chars', s['chars']), s.get('summarized', False))
```

Check:
- `models_dev_api` - should be summarized; if not, flag as high-priority waste (~3.5k tokens raw)
- `copilot_catalog`, `opencode_catalog`, `lifecycle`, `views` - should be skeletonized; if full blobs, flag
- Largest unsummarized sources by chars

### 6. Prompt analysis

```bash
wc -c prompt.system.txt prompt.user.txt
```

Scan `prompt.user.txt` for:
- `models_dev_api` section: if it contains YAML with `name:`, `family:`, `modalities:` fields, it is raw and wasteful
- Catalog sources: if `copilot_catalog` section contains full prose lines beyond `` `id=... `` lines, it is not skeletonized

### 7. Output quality

Read `outputs.index.json` for expected keys. For each output file:
- Verify file exists in `outputs/`
- Check for truncation: file ends abruptly mid-record
- Sample 3-5 model IDs from `sources/02_copilot_catalog.txt` and verify they appear in the corresponding output

```bash
grep "id=" sources/02_copilot_catalog.txt | head -5
grep "claude-sonnet-4.6" outputs/docs/models/models.catalog.copilot.md
```

### 8. LLM response quality

```bash
head -c 2 llm.response.txt   # should be {
tail -c 2 llm.response.txt   # should be }
```

```python
import json
try:
    data = json.loads(open('llm.response.txt').read())
    print("valid JSON, keys:", list(data.keys()))
except Exception as e:
    print("INVALID JSON:", e)
```

Cross-check keys against `outputs.index.json` expected output paths.

### 9. Summarizer output quality

`summarizer.calls.json` does not include summary text. Evaluate quality by reading the summarized source blobs from `sources/` and checking for presence of critical facts:

```bash
grep -i "claude\|gpt\|gemini\|release_date\|eol\|context" sources/07_copilot_supported_models.txt | head -20
```

Verify preservation of: model IDs, provider names, release/EOL/knowledge dates, context/input/output limits, cost values.

## Report Format

Write the report to `analysis.<run_id>.md` in the run directory, where `<run_id>` is the run directory basename (e.g. `20260322T111818Z`). Use markdown with headers and tables. After writing, print the output path.

```markdown
# Run Analysis: <run_id>

## Run Summary
- model: ...
- status: success/failed
- total_time: Xs

## Time Breakdown
| step | duration | % of total |
|---|---|---|
| read_sources | Xs | N% |
| call_llm | Xs | N% |

## Token Spend
| stage | input_tokens | output_tokens |
|---|---|---|
| summarizer (×N) | ... | ... |
| main LLM | ... | ... |
| total | ... | ... |

## Summarizer Efficiency
| source | tokens_in | tokens_out | compression | quality |
|---|---|---|---|---|

## Source Sizes
| source | chars | raw_chars | summarized | notes |
|---|---|---|---|---|

**Largest unsummarized:** ...

## Prompt
- system: N chars
- user: N chars (~N tokens est.)

## Output Quality
- expected_outputs: [list from outputs.index.json]
- issues: [truncation / missing keys / JSON parse errors / hallucinated fields]

## Optimization Opportunities
1. ... (~N tokens)
2. ... (~N tokens)
```

## Key Thresholds

| metric | good | poor |
|---|---|---|
| summarizer compression | ≥50% | <40% |
| models_dev_api | summarized | raw (~3.5k tokens wasted) |
| catalog sources as prompt input | skeletonized | full blob (~2k tokens wasted each) |
| LLM response | valid JSON, all keys present | missing keys, truncated, parse error |
| total pipeline time | <5 min | >10 min |
| main LLM input tokens | <20k | >30k |
| read_sources wall time | <60s | >120s (check summarizer parallelism) |
