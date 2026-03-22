# GitHub Copilot Catalog
> updated: 2026-03-21
> scope: normalized raw records only
> derived outputs: models.lifecycle.md, models.views.md
> keys: see models.md and models.schema.yaml

## Anthropic

### Claude Opus
- id=claude-opus-4.6 | st=active | rel=2026-02-05 | ctx=144K | out=64K | in=128K | rsn=basic | tools=y | mult=3x | best=deep reasoning and debugging | sig=sophisticated reasoning; flagship Claude Opus | caut=high premium cost
- id=claude-opus-4.6-fast-mode | st=preview | ctx=unk | rsn=unk | tools=unk | mult=30x | best=deep reasoning and debugging | sig=fast mode variant | caut=very high premium cost; incomplete specs | fb=claude-opus-4.6
- id=claude-opus-4.5 | st=active | rel=2025-11-24 | ctx=160K | out=32K | in=128K | rsn=basic | tools=y | mult=3x | best=deep reasoning and debugging | sig=strong complex problem solving | caut=high premium cost | fb=claude-opus-4.6
- id=claude-opus-4.1 | st=retired | rel=2025-08-05 | eol=2026-02-17 | repl=claude-opus-4.6 | ctx=80K | out=16K | rsn=basic | tools=n | best=legacy reasoning | sig=older Opus release | caut=retired; no tool calling | fb=claude-opus-4.6
- id=claude-opus-4 | st=retired | eol=2025-10-23 | repl=claude-opus-4.6 | best=legacy reasoning | sig=older Opus generation | caut=retired | fb=claude-opus-4.6

### Claude Sonnet
- id=claude-sonnet-4.6 | st=active | rel=2026-02-17 | ctx=200K | out=32K | in=128K | rsn=basic | tools=y | mult=1x | best=general-purpose coding and agent tasks; deep reasoning and debugging | sig=balanced coding workflow model; broad Copilot support | caut=not included in some clients
- id=claude-sonnet-4.5 | st=active | rel=2025-09-29 | ctx=144K | out=32K | in=128K | rsn=basic | tools=y | mult=1x | best=general-purpose coding and agent tasks | sig=balanced reasoning and coding | caut=older than 4.6 | fb=claude-sonnet-4.6
- id=claude-sonnet-4 | st=active | rel=2025-05-22 | ctx=216K | out=16K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=performance and practicality balance | caut=older than 4.6 | fb=claude-sonnet-4.6
- id=claude-sonnet-3.7 | st=retired | eol=2025-10-23 | repl=claude-sonnet-4.6 | best=legacy reasoning | sig=older Sonnet generation | caut=retired | fb=claude-sonnet-4.6
- id=claude-sonnet-3.7-thinking | st=retired | eol=2025-10-23 | repl=claude-sonnet-4.6 | best=legacy reasoning | sig=thinking-tuned Sonnet variant | caut=retired | fb=claude-sonnet-4.6
- id=claude-sonnet-3.5 | st=retired | eol=2025-11-06 | repl=claude-haiku-4.5 | best=legacy coding help | sig=older Sonnet release | caut=retired | fb=claude-haiku-4.5

### Claude Haiku
- id=claude-haiku-4.5 | st=active | rel=2025-10-15 | ctx=144K | out=32K | in=128K | rsn=basic | tools=y | mult=0.33x | best=fast help with simple or repetitive tasks | sig=low-cost Claude option; fast lightweight answers | caut=less capable than Sonnet or Opus for hardest tasks

## Google

### Gemini 3
- id=gemini-3.1-pro | st=preview | rel=2026-02-19 | ctx=128K | out=64K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=high tool precision; efficient edit-test loops | caut=preview; limited client availability
- id=gemini-3-pro | st=preview | rel=2025-11-18 | ctx=128K | out=64K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=strong code generation and research workflows | caut=preview | fb=gemini-3.1-pro
- id=gemini-3-flash | st=preview | rel=2025-12-17 | ctx=128K | out=64K | in=128K | rsn=basic | tools=y | mult=0.33x | best=fast help with simple or repetitive tasks | sig=low-cost fast Gemini option | caut=preview; less depth than Pro variants

### Gemini 2.5
- id=gemini-2.5-pro | st=active | rel=2025-03-20 | ctx=128K | out=64K | in=128K | rsn=none | tools=y | mult=1x | best=deep reasoning and debugging | sig=strong debugging and research workflows | caut=not included in Copilot CLI

### Gemini 2.0
- id=gemini-2.0-flash | st=retired | eol=2025-10-23 | repl=gemini-2.5-pro | best=legacy fast help | sig=older Gemini Flash model | caut=retired | fb=gemini-2.5-pro

## OpenAI

### GPT-4
- id=gpt-4.1 | st=active | rel=2025-04-14 | ctx=128K | out=16K | in=64K | rsn=none | tools=y | mult=0x | best=general-purpose coding and writing | sig=included model; broad client support | caut=older than GPT-5 family
- id=gpt-4o | st=deprecated | rel=2024-05-13 | ctx=128K | out=4K | in=64K | rsn=none | tools=y | mult=0x | best=legacy multimodal help | sig=included zero-multiplier model | caut=not listed in current supported models | fb=gpt-4.1

### GPT-5 Base
- id=gpt-5.4 | st=active | rel=2026-03-05 | ctx=400K | out=128K | in=272K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=largest GPT-5 base context in Copilot | caut=costlier than mini variants
- id=gpt-5.4-mini | st=active | rel=2026-03-17 | ctx=400K | out=128K | in=272K | rsn=basic | tools=y | mult=0.33x | best=agentic software development | sig=cheap large-context GPT-5 variant; good for codebase exploration | caut=less depth than full gpt-5.4
- id=gpt-5.2 | st=active | rel=2025-12-11 | ctx=264K | out=64K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=replacement for retired gpt-5 | caut=older than gpt-5.4 | fb=gpt-5.4
- id=gpt-5.1 | st=active | rel=2025-11-13 | ctx=264K | out=64K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=strong multi-step problem solving | caut=older than gpt-5.2 and gpt-5.4 | fb=gpt-5.4
- id=gpt-5-mini | st=active | rel=2025-08-13 | ctx=264K | out=64K | in=128K | rsn=basic | tools=y | mult=0x | best=general-purpose coding and writing; deep reasoning and debugging | sig=included GPT-5 tier; fast and broadly available | caut=less capable than larger GPT-5 models for hardest problems
- id=gpt-5 | st=retired | rel=2025-08-07 | eol=2026-02-17 | repl=gpt-5.2 | ctx=128K | out=128K | rsn=basic | tools=y | best=legacy reasoning | sig=first GPT-5 release | caut=retired | fb=gpt-5.2

### GPT-5 Codex
- id=gpt-5.3-codex | st=active | rel=2026-02-24 | ctx=400K | out=128K | in=272K | rsn=basic | tools=y | mult=1x | best=agentic software development; general-purpose coding and writing | sig=latest Codex agent model | caut=premium model
- id=gpt-5.2-codex | st=active | rel=2025-12-11 | ctx=400K | out=128K | in=272K | rsn=basic | tools=y | mult=1x | best=agentic software development | sig=agentic tasks | caut=older than gpt-5.3-codex | fb=gpt-5.3-codex
- id=gpt-5.1-codex-max | st=active | rel=2025-12-04 | ctx=400K | out=128K | in=128K | rsn=basic | tools=y | mult=1x | best=agentic software development | sig=max Codex variant | caut=older than gpt-5.3-codex | fb=gpt-5.3-codex
- id=gpt-5.1-codex | st=active | rel=2025-11-13 | ctx=400K | out=128K | in=128K | rsn=basic | tools=y | mult=1x | best=deep reasoning and debugging | sig=strong architecture analysis; broad tool use | caut=older than newer Codex models | fb=gpt-5.3-codex
- id=gpt-5.1-codex-mini | st=preview | rel=2025-11-13 | ctx=400K | out=128K | in=128K | rsn=basic | tools=y | mult=0.33x | best=deep reasoning and debugging | sig=low-cost Codex preview | caut=preview; reduced capability vs full Codex variants | fb=gpt-5.3-codex
- id=gpt-5-codex | st=retired | eol=2026-02-17 | repl=gpt-5.2-codex | best=legacy agentic coding | sig=older Codex release | caut=retired | fb=gpt-5.2-codex

### Legacy Reasoning
- id=o4-mini | st=retired | eol=2025-10-23 | repl=gpt-5-mini | best=legacy lightweight reasoning | sig=older OpenAI reasoning line | caut=retired | fb=gpt-5-mini
- id=o3-mini | st=retired | eol=2025-10-23 | repl=gpt-5-mini | best=legacy lightweight reasoning | sig=older OpenAI reasoning line | caut=retired | fb=gpt-5-mini
- id=o3 | st=retired | eol=2025-10-23 | repl=gpt-5.2 | best=legacy deep reasoning | sig=older OpenAI reasoning line | caut=retired | fb=gpt-5.2
- id=o1-mini | st=retired | eol=2025-10-23 | repl=gpt-5-mini | best=legacy lightweight reasoning | sig=older OpenAI reasoning line | caut=retired | fb=gpt-5-mini

## xAI

### Grok Code
- id=grok-code-fast-1 | st=active | rel=2025-08-27 | ctx=128K | out=64K | in=128K | rsn=basic | tools=y | mult=0.25x | best=general-purpose coding and writing | sig=very low premium cost; fast coding help | caut=not available in Copilot CLI

## Unclassified

### Experimental / Unconfirmed
- id=raptor-mini | st=preview | mult=0x | best=general-purpose coding and writing | sig=fine-tuned GPT-5 mini; included for some plans | caut=coming soon; incomplete specs | fb=gpt-5-mini
- id=goldeneye | st=preview | best=deep reasoning and debugging | sig=fine-tuned GPT-5.1-Codex | caut=incomplete specs; limited availability | fb=gpt-5.1-codex
- id=qwen2.5 | st=unconfirmed | best=general-purpose coding and writing | sig=listed in comparison page only | caut=provider and support status unverified
