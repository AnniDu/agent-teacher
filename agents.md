# AGENTS.md

# Agent Teacher Development Guide

This document defines the engineering workflow for AI agents working in this repository.

---

# Source of Truth

The repository follows the following priority order:

1. GitHub Issue
2. Accepted RFC
3. Pull Request Review Comments
4. Existing Repository Architecture

Implementation should always follow the highest-priority applicable document.

Do not invent requirements beyond the documented scope.

---

# Workflow

Before implementing any task:

1. Read the referenced GitHub Issue.
2. If the Issue references an RFC, read the accepted RFC.
3. Review the existing implementation before making changes.

Before writing code, briefly summarize:

* Issue goal
* Scope
* Non-goals
* High-level implementation plan

---

# Implementation Principles

* Implement only the requested Issue.
* Do not expand the scope.
* Do not perform opportunistic refactoring.
* Follow the accepted RFC when one exists.
* Preserve existing architecture and module boundaries.
* Prefer simple and maintainable solutions.
* Avoid introducing unnecessary abstractions.
* Do not modify unrelated files.

---

# Testing

For every implementation:

* Add or update tests for new behavior.
* Ensure existing tests continue to pass.
* Run the full test suite before finishing.

Do not skip testing unless explicitly instructed.

---

# Git Workflow

For new work:

* Create a feature branch.
* Commit with a clear commit message.
* Push the branch.
* Open a Pull Request referencing the GitHub Issue.

If a Pull Request already exists for the Issue:

* Read all review comments.
* Address every actionable review comment.
* Push additional commits to the existing branch.
* Do not create a new Pull Request.

---

# Pull Request Expectations

Every Pull Request should include:

* Summary
* Related Issue
* Related RFC (if applicable)
* Testing
* Non-goals

---

# Engineering Philosophy

This project values:

* Small, focused changes
* Incremental evolution
* Clear module boundaries
* Simple designs
* Production-quality code
* Well-tested implementations

Favor proven engineering practices over unnecessary complexity.

---

# Validation

At the beginning of every implementation task, confirm:

* Which Issue is being implemented.
* Whether an RFC applies.
* The implementation scope.
* The non-goals.

Only begin implementation after this summary has been provided.
