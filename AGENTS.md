# AGENTS.md

## Project Operating Mode

This project uses disciplined AI-assisted engineering.

The AI agent must not behave like a free-form coding assistant. It must follow context-driven, spec-driven, task-driven, review-driven development.

## Core Rules

1. Context before implementation.
2. Spec before code.
3. Plan before patch.
4. One small task at a time.
5. No unrelated refactoring.
6. No dependency changes without approval.
7. No database/schema changes without approval.
8. No destructive commands without approval.
9. Every code change requires tests, evals, or manual verification.
10. Every completed task must include changed files, verification result, risks, and rollback plan.

## Required Workflow

For new features:

1. Run `/project_bootstrap` if project context is missing.
2. Run `/iteration_kickoff`.
3. Create brief, spec, plan, and tasks.
4. Wait for approval.
5. Run `/implement_task` one task at a time.
6. Run `/run_evals` if AI behavior is affected.
7. Run `/review_and_ship`.
8. Run `/retro_update_rules`.

For legacy projects:

1. Run `/legacy_scout`.
2. Create project map, risk map, test inventory, and safe first tasks.
3. Add characterization tests before behavior changes.
4. Make minimal, reversible changes only.

## Git Rules

- Never work directly on main/master unless explicitly approved.
- Use one branch per iteration.
- Do not commit unless the user explicitly says to commit.
- Before final summary, report git status and changed files.

## Final Report Format

Every completed task must report:

- Iteration ID
- Spec used
- Task ID
- Changed files
- Tests run
- Evals run, if applicable
- Verification result
- Remaining risks
- Rollback plan
- Recommended next action