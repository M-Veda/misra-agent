# Architecture

Client

↓

FastAPI

↓

Analysis Pipeline

↓

Parser

↓

AST

↓

CFG

↓

Cppcheck

↓

Rule Discovery

↓

Rule Engine

↓

Violation Collection

↓

AI Explanation

↓

Patch Engine

↓

Patch Validator

↓

Compliance Validator

↓

Report Generator

↓

Database

↓

Frontend

---

Rules

Parser never generates fixes.

Rule engine never modifies source code.

Patch engine never parses code.

Validators never generate fixes.

Reports never execute rules.

API never contains business logic.

---

Every module should have one responsibility.

No circular imports.

No duplicated logic.

No hidden dependencies.