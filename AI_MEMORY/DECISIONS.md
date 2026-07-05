# Architectural Decisions

Decision 1

Business logic must never be placed inside API routes.

Reason

Maintain separation of concerns.

---

Decision 2

Rule implementations remain independent.

Reason

Future scalability.

---

Decision 3

Parser never modifies source code.

Reason

Single Responsibility Principle.

---

Decision 4

Validators never generate fixes.

Reason

Maintain deterministic validation.

---

Decision 5

Always modify existing modules before creating new files.

Reason

Avoid architecture fragmentation.

---

Append future architectural decisions here.