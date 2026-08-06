# PPTSmith PMO Private Bundle

This private delivery combines the current MeowClaw PPT Smith engine with the
private PMO production pack.

## Identity

Single source of truth: `packaging/identity.json` and `VERSION`, enforced by
`scripts/check_identity.py`. The values below are restated for reading
convenience; if they ever disagree with the identity document, the document wins
and the check fails.

- Root Skill: `article-html-to-ppt`
- Display name: MeowClaw PPT Smith
- Engine version: `2.3.0`
- Private extension: `private-pmo-pack/`
- Private PMO implementation status: Phase 2 P0 verified

## Bundle hygiene and audit

The bundle audit is generated, not handwritten. Run:

```bash
python3 scripts/audit_bundle.py --fail-on-finding
```

It writes `references/BUNDLE-AUDIT.json` (source of truth) and
`references/BUNDLE-AUDIT.md`, checking excluded-path presence, absolute path
leaks, secret assignments, secret-shaped filenames, and undeclared high-entropy
strings. Deliberate exceptions live in `packaging/audit-allowlist.json` and must
carry a reason; the report lists every suppression with that reason.

`scripts/normalize_bundle_paths.py` rewrites recorded local absolute paths to
bundle-relative paths and is the fix for `BUNDLE_ABSOLUTE_PATH_LEAK`.

The root `SKILL.md` remains the canonical PPTSmith workflow. For PMO or project
visualization work, also load:

- `private-pmo-pack/state/component-system-progress.json`
- `private-pmo-pack/docs/pmo-component-system-roadmap.md`
- `private-pmo-pack/contracts/mckinsey-pmo.style.json`

## Input

The bundle accepts:

1. Narrative source material such as an article, PRD, project brief, weekly
   report, or meeting notes.
2. A project evidence bundle containing schedules, KPI data, risks, actions,
   RACI, budgets, or system exports.
3. Structured PMO JSON matching schemas under `private-pmo-pack/schemas/`.

Do not invent missing PMO facts. Extract evidence, identify missing dates,
owners, targets, statuses, and decisions, then generate only components with
sufficient support.

## Verified private components

Phase 1:

- annotated doughnut;
- phased Roadmap;
- Gantt timeline.

Phase 2 P0:

- KPI/status;
- milestone timeline;
- risk heat map;
- RACI matrix.

The direct PMO v0.1 renderer also contains the ten established page families:
Executive Dashboard, Roadmap, Milestone, RAID, Workstream, RACI, Risk Heat Map,
Decision, KPI Dashboard, and Action Tracker.

Phase 2 P1/P2 and Phase 3 entries are planned until the state file and QA
evidence explicitly mark them verified.

## Commands

Run from `private-pmo-pack/`:

```bash
python3 scripts/build_component_system_phase1.py
python3 scripts/verify_component_system_phase1.py
python3 scripts/build_component_system_phase2.py
python3 scripts/verify_component_system_phase2.py
python3 scripts/build_pmo_deck.py
python3 scripts/verify_pmo_deck.py
python3 -m pytest -q
```

Run from the bundle root:

```bash
python3 -m pytest -q                                   # engine suite
python3 scripts/check_identity.py                      # identity consistency
python3 scripts/audit_bundle.py --mode worktree --fail-on-finding
```

Use `pytest`, not `unittest discover`, at the bundle root: the `tests/` tree has
no `__init__.py`, so `unittest discover -s tests` collects zero tests there and
reports a misleading `OK`.

## Included evidence

- Phase 1 native editable PPTX and compact render PNG evidence.
- Phase 2 P0 native editable PPTX and compact render PNG evidence.
- PMO v0.1 sample PPTX and structural QA summaries.
- Semantic schemas, examples, fixtures, tests, builders, verifiers, taxonomy,
  routing, quality, and state files.

Large duplicate PDFs, obsolete render caches, browser brainstorming sessions,
Python caches, and temporary work directories are intentionally excluded.

## Delivery gates

- Use native PowerPoint objects for message-bearing content.
- Never deliver a screenshot-only or whole-slide-raster PMO page.
- Verify data-to-label and data-to-position ownership after rendering.
- Run package inspection and real render review before claiming final.
- Preserve the distinction among planned, created, rendered, verified, final,
  and blocked.

## Known limits

- Native connector endpoint binding is not claimed without XML proof.
- LibreOffice render evidence does not guarantee Microsoft PowerPoint pixel
  parity.
- The strict complete PMO JSON schema is a renderer contract, not the only
  user intake method.
- This bundle is private commercial material. Do not publish it to GitHub,
  ClawHub, Xiaping, or another registry.

## Skill Workshop status

A dedicated wrapper Skill proposal was created as
`pptsmith-pmo-private-20260724-8caf7c18e5`. Its application approval timed out,
so it remains pending and is not represented as installed in this archive.
This archive is immediately usable through the verified root PPTSmith Skill and
the bundled private PMO reference path above.
