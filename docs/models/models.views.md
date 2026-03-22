# Model Views
> updated: 2026-03-21
> scope: quick recommendations and summary picks
> source: generated from models.catalog.copilot.md and models.catalog.opencode.md
> note: excludes retired models and models retiring within 30 days; use catalog shards for raw facts and edge cases

## By Cost

### Lowest Copilot multiplier
- 0x: gpt-4.1, gpt-5-mini, raptor-mini
- 0.25x: grok-code-fast-1
- 0.33x: claude-haiku-4.5, gemini-3-flash, gpt-5.1-codex-mini, gpt-5.4-mini
- 1x: claude-sonnet-4, claude-sonnet-4.5, claude-sonnet-4.6, gemini-2.5-pro, gemini-3-pro, gemini-3.1-pro, gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-max, gpt-5.2, gpt-5.2-codex, gpt-5.3-codex, gpt-5.4
- 3x: claude-opus-4.5, claude-opus-4.6
- 30x: claude-opus-4.6-fast-mode

### Lowest OpenCode Go estimated cost per request
- minimax-m2.5: ~$0.0006
- minimax-m2.7: ~$0.0009
- kimi-k2.5: ~$0.0065
- glm-5: ~$0.0104

## By Task

### General-purpose coding and writing
- gpt-5-mini
- gpt-4.1
- grok-code-fast-1
- claude-sonnet-4.5
- claude-sonnet-4.6
- glm-5
- minimax-m2.7

### Fast help with simple or repetitive tasks
- claude-haiku-4.5
- gemini-3-flash
- grok-code-fast-1
- minimax-m2.5

### Deep reasoning and debugging
- gpt-5.4
- gpt-5.2
- gpt-5.1
- claude-opus-4.6
- claude-sonnet-4.6
- gemini-2.5-pro
- gemini-3.1-pro
- gemini-3-pro
- glm-5
- kimi-k2.5

### Agentic software development
- gpt-5.3-codex
- gpt-5.2-codex
- gpt-5.1-codex-max
- gpt-5.4-mini
- claude-sonnet-4.6

### Long-context work
- gpt-5.4
- gpt-5.4-mini
- gpt-5.3-codex
- gpt-5.2-codex
- kimi-k2.5
- minimax-m2.7
- minimax-m2.5

## Workflow

### Cheapest viable defaults
- Copilot: gpt-5-mini for broad included use; grok-code-fast-1 for low premium cost; claude-haiku-4.5 for fast Claude responses
- OpenCode Go: minimax-m2.5 for cheapest routine work; minimax-m2.7 for cheap newer default

### Best coding depth
- gpt-5.4 for broad reasoning and large context
- claude-opus-4.6 for hardest reasoning-heavy debugging
- gemini-3.1-pro for tool-precise edit-test loops
- kimi-k2.5 for long-context reasoning outside Copilot

### Best agent workflow picks
- gpt-5.3-codex as primary Codex choice
- gpt-5.2-codex as solid fallback
- gpt-5.4-mini when you want large context at lower cost
- claude-sonnet-4.6 for balanced coding plus agent tasks

### Conservative stable picks
- gpt-4.1
- gpt-5-mini
- claude-sonnet-4.6
- claude-opus-4.6
- gemini-2.5-pro
- minimax-m2.7

### Preview-only picks when you want newest behavior
- gemini-3-flash
- gemini-3-pro
- gemini-3.1-pro
- gpt-5.1-codex-mini
- claude-opus-4.6-fast-mode
- raptor-mini
- goldeneye
