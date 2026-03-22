# OpenCode Go Catalog
> updated: 2026-03-21
> scope: normalized raw records only
> derived outputs: models.lifecycle.md, models.views.md
> keys: see models.md and models.schema.yaml

## ZhipuAI

### GLM
- id=glm-5 | st=active | rel=2026-02-11 | ctx=204.8K | out=128K | rsn=basic | tools=y | est=~$0.0104 | rate=in:1,out:3.2,cache_read:0.2 per 1M tokens; shared pool ~$12/5hr, $30/week, $60/month | best=general-purpose coding and reasoning | sig=largest GLM option in OpenCode Go | caut=higher cost than MiniMax models | fb=use balance

## Moonshot AI

### Kimi
- id=kimi-k2.5 | st=active | rel=2026-01-27 | ctx=256K | out=64K | rsn=basic | tools=y | est=~$0.0065 | rate=in:0.6,out:3,cache_read:0.1 per 1M tokens; shared pool ~$12/5hr, $30/week, $60/month | best=long-context coding and reasoning | sig=largest context among listed OpenCode Go models | caut=costlier than MiniMax models | fb=use balance

## MiniMax

### M2
- id=minimax-m2.7 | st=active | rel=2026-03-18 | ctx=204.8K | out=128K | rsn=basic | tools=y | est=~$0.0009 | rate=in:0.3,out:1.2,cache_read:0.06 per 1M tokens; shared pool ~$12/5hr, $30/week, $60/month | best=low-cost coding and reasoning | sig=best request economy in current OpenCode Go set; newest release | caut=less external guidance than larger ecosystems | fb=use balance
- id=minimax-m2.5 | st=active | rel=2026-02-12 | ctx=204.8K | out=128K | rsn=basic | tools=y | est=~$0.0006 | rate=in:0.3,out:1.2,cache_read:0.03 per 1M tokens; shared pool ~$12/5hr, $30/week, $60/month | best=lowest-cost routine coding | sig=cheapest model in current OpenCode Go set | caut=older than minimax-m2.7 | fb=minimax-m2.7
