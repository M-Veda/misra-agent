# AI Instructions

You are contributing to a production-grade MISRA C:2012 Compliance Platform.

## Primary Goal

Build an enterprise-level static analysis platform capable of:

- Detecting MISRA C:2012 violations
- Explaining violations
- Automatically generating compliant fixes
- Validating generated fixes
- Producing professional compliance reports

The platform must remain modular, maintainable, extensible and production-ready.

---

## General Rules

Always inspect the existing repository before making changes.

Never rewrite working code.

Never duplicate existing functionality.

Always reuse existing modules.

Preserve backward compatibility.

Maintain all existing APIs.

Never introduce placeholder implementations.

Never leave TODO comments.

Every feature must be fully functional.

---

## Coding Standards

Follow PEP8.

Use type hints.

Use dataclasses when appropriate.

Prefer composition over inheritance.

Avoid global variables.

Keep functions small.

Write descriptive docstrings.

---

## Architecture Rules

Do not place business logic inside API routes.

API routes should only:

- validate requests
- call services
- return responses

Business logic belongs inside services.

Rule logic belongs inside the rule engine.

Fix generation belongs inside the patch engine.

Validation belongs inside validators.

Reporting belongs inside report generators.

---

## Error Handling

Every module must:

- log failures
- raise meaningful exceptions
- never silently ignore errors

---

## Logging

Every analysis receives:

Analysis ID

Each stage logs:

- start
- finish
- duration
- warnings
- failures

---

## Performance

Avoid unnecessary parsing.

Reuse parsed AST.

Cache intermediate data when possible.

Support future parallel execution.

---

## Testing

Every new feature requires:

- unit tests
- integration tests where applicable

Existing tests must continue passing.

---

## File Modification Rules

Modify existing files whenever possible.

Only create new files when architecture genuinely requires them.

Avoid duplicate helper utilities.

---

## Before Finishing

Always provide:

- implementation summary
- files modified
- design decisions
- validation performed
- possible regression risks

Never claim a feature is complete unless it is fully implemented.