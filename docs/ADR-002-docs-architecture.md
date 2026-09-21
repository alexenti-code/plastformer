# ADR-002 — Docs architecture: strict file semantics + public/internal split

**Status:** ACTIVE — семантика файлов и граница публичного/внутреннего.
**Date:** 2026-09-05. **Owner:** Alex. **Author role:** docs architect (agent).

**Опирается на:** [CONSTITUTION.md](CONSTITUTION.md).

## 1. Strict file semantics

| File | Semantics | May contain | Must NOT contain |
|---|---|---|---|
| `docs/THEORY.md` + `THEORY.ru.md` v4.1 | mechanisms description only | multi-tau decay, two clocks, reconcile, background tick as core-without-input, cascade anchors, descriptive act/time accounts | must/forbidden norms, "Violated if" tests, axioms, permissions, punishments |
| `docs/GLOSSARY.md` v4.2 | pure dictionary | term → definition (EN with RU term in brackets) | axioms, permissions, punishments, norms, "Violated if" |
| `docs/MANIFEST.md` v4.2 | outward declaration only | claim, positioning, lineage, working-name note, honest boundary, research questions | enforceable norms, notes about replaced wording |
| `docs/CONSTITUTION.md` | binding norms | postulates O-1…O-10 and checks C1–C8, each = statement + "Violated if" test; precedence header | mechanisms exposition, dictionary entries, lineage narrative |
| `AGENTS.md` (repo root, PUBLIC) | agent read order, file map, forbidden patterns, commit discipline | public, harmless instructions | secrets, internal paths, unpublished results |
| `drafts/rebuild-private/` (gitignored) | what NEVER goes public | private working layer: ТЗ, cards, journal, snapshots | — (never published) |

Precedence: **CONSTITUTION > ADR > preprint / E1 / SPEC / code**.

## 2. Public/internal boundary

- **Public:** conceptual architecture, terms, core distinctions, high-level evaluation direction, limited experimental code for controlled refutation tests.
- **Never public unless explicitly published in a later signed release:** exact parametric-update mechanisms; learning objectives/loss/update schedules; topologies/tensor layouts/layer placement; temporal-binding/interference/consolidation mechanisms; proprietary datasets, private evaluation records, commercial deployment data; production infra, credentials, integrations, client info, operational policies; trade-secret / patent-subject implementation details.
- **Private layer:** the working layer `drafts/rebuild-private/` — ТЗ, cards, journal, snapshots; and `inputs/`.

Rule: when in doubt, keep local. Enforcement: `.gitignore` excludes `inputs/` and `drafts/rebuild-private/`.

## 3. What this ADR does NOT do

- No publication step: this project publishes nothing; the private directory stays local.
- No terminology changes beyond those recorded in this project.
