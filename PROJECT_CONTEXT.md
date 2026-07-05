# Project Context

Project Name

MISRA AI Compliance Platform

---

Purpose

An AI-powered static analysis platform for MISRA C:2012.

The application should:

- Parse C source files
- Build AST
- Execute MISRA rule engine
- Integrate Cppcheck
- Detect violations
- Generate AI-assisted explanations
- Automatically generate compliant fixes
- Validate fixes
- Generate compliance reports

---

Technology Stack

Backend

- FastAPI

Frontend

- Streamlit

Parser

- Clang

Static Analysis

- Cppcheck

Database

- SQLite

AI

- LLM-based explanation and fix generation

Testing

- pytest

---

Current Architecture

- Parser
- Rule Engine
- Patch Engine
- Validator
- Report Generator
- AI Module
- Database
- API
- Frontend

---

Development Philosophy

Enterprise architecture

Modular design

Low coupling

High cohesion

Dependency injection

Extensible rule engine

Production quality

---

Development Priority

1. Stability

2. Correctness

3. Maintainability

4. Performance

5. UI

---

Never sacrifice architecture for short-term implementation speed.