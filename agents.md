# AGENTS.md

# Agent Teacher Engineering Workflow

This document defines how AI agents work in this repository.

Its purpose is to ensure every implementation follows a consistent engineering workflow and produces small, reviewable, production-quality changes.

---

# 1. Source of Truth

When multiple sources exist, follow them in the following priority order:

1. GitHub Issue
2. Accepted RFC
3. Pull Request Review Comments
4. Existing Repository Architecture

If two sources conflict, always follow the higher-priority source.

Do not invent requirements beyond the documented scope.

---

# 2. Decision Process

Before writing any code, make the following decisions in order.

## Step 1 — Does this Issue require an RFC?

An RFC is required if the change:

* introduces a new module
* changes module boundaries
* changes public interfaces
* changes state or data schemas
* changes runtime workflow
* introduces new infrastructure or external systems
* affects multiple subsystems

If an RFC is required but no accepted RFC exists:

* Draft an RFC under `docs/rfcs/`
* Stop after creating the RFC
* Do not implement code

Otherwise:

* Continue implementation directly.

---

## Step 2 — Determine the branch strategy

By default:

* Create branches from `dev_v1`.

If the Issue explicitly depends on an unmerged feature branch:

* Create the branch from that feature branch.
* Use stacked Pull Requests.

---

## Step 3 — Validate understanding

Before implementation, summarize:

* Issue goal
* Scope
* Non-goals
* High-level implementation plan

Only begin implementation after this summary.

---

# 3. Development Workflow

For every implementation:

1. Read the GitHub Issue.
2. Read the accepted RFC (if one exists).
3. Review the existing implementation.
4. Create the appropriate branch.
5. Implement the requested Issue.
6. Add or update tests.
7. Run the complete test suite.
8. Commit the changes.
9. Push the branch.
10. Open a Pull Request.

If updating an existing Pull Request:

1. Read every review comment.
2. Address every actionable comment.
3. Push additional commits.
4. Do not create a new Pull Request.

---

# 4. Branch Strategy

## Naming

Use deterministic branch names.

```
feature/issue-<number>-<short-slug>
fix/issue-<number>-<short-slug>
docs/issue-<number>-<short-slug>
chore/issue-<number>-<short-slug>
```

Examples:

```
feature/issue-1-memory-store
fix/issue-5-llm-retry
docs/issue-7-agents-md
```

Avoid generic names such as:

```
feature/update
feature/work
fix/bug
implementation
codex/changes
```

Feature branches are temporary.

After a feature is merged, future work should be performed in a new feature or fix branch.

---

# 5. Implementation Rules

* Implement only the requested Issue.
* Stay within the documented scope.
* Do not perform opportunistic refactoring.
* Prefer extending existing patterns over introducing new ones.
* Preserve existing architecture and module boundaries.
* Prefer the simplest solution that satisfies the Issue.
* Do not optimize prematurely.
* Do not introduce third-party dependencies unless explicitly required by the Issue or an accepted RFC.
* Do not modify unrelated files.
* When requirements or architecture are unclear, stop and ask for clarification instead of making assumptions.
* If implementing the requested change would significantly expand the current Issue, recommend creating a new Issue instead of expanding scope.

---

# 6. Pull Requests

Every Pull Request should:

* reference the related GitHub Issue
* reference the RFC (if applicable)
* summarize the implementation
* summarize testing performed
* explicitly state non-goals

Pull Requests should be:

* small
* focused
* independently reviewable

---

# 7. Engineering Principles

This repository values:

* incremental development
* small, reviewable changes
* clear module boundaries
* production-quality implementations
* comprehensive testing
* consistency over cleverness
* proven solutions over unnecessary complexity
