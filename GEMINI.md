# Development Rules

- **Workflow:** Always use Test-Driven Development (TDD). Write the test first, verify failure, then implement.
- **Documentation:** Only update documentation (READMEs, logs, etc.) at the **end** of a completed task. Do not update docs for every incremental step.
- **Conciseness:** Be extremely brief. Skip conversational fillers and summaries of completed tool calls.
- **Permissions:** Do not ask for confirmation for read-only commands (ls, cat, grep, find).
- **Task Execution:** If a task has multiple logical steps, execute them sequentially without stopping to report progress unless an error occurs.
- **Database changes:** Do not make changes to the database schema without first having a migratino strategy and checking how can it affect the current stored data.
