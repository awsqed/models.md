---
name: conventional-commit
description: Guide for writing Conventional Commit messages from staged changes, including type, optional scope, and clear subject/body structure.
---

Use this skill when preparing commit messages for staged changes.

## Goal

Produce clear, scoped commit messages that follow Conventional Commits and reflect the actual diff.

## Required workflow

1. Review staged changes
   - `git --no-pager diff --staged --name-only`
   - `git --no-pager diff --staged`

2. Pick commit type based on impact
   - `feat`: user-facing feature
   - `fix`: bug fix
   - `docs`: documentation only
   - `refactor`: internal change without behavior change
   - `test`: tests only
   - `build`: build or dependency tooling
   - `ci`: CI or workflow changes
   - `chore`: maintenance not fitting above

3. Choose optional scope from the primary changed area
   - examples: `docs`, `pipeline`, `sources`, `llm`, `output`, `config`

4. Write the subject in imperative mood, 72 chars or less

5. Add a body only when useful
   - what changed
   - why it changed
   - notable behavior or migration impact

## Format

`<type>(<scope>): <short summary>`

Examples:

- `docs(models): update pipeline entrypoint commands`
- `fix(sources): validate url source value and urls exclusivity`
- `refactor(pipeline): extract step logging wrapper`

Optional body template:

```text
<type>(<scope>): <short summary>

- <change 1>
- <change 2>
```

## Do / Don't

- Do align the message with the staged diff only.
- Do split unrelated changes into separate commits.
- Don't use vague subjects like `update stuff` or `fix issues`.
- Don't mark breaking changes unless there is an actual API or behavior break.
