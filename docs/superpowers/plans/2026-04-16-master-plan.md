# TIMS Production Readiness — Master Plan

**Project:** Tertiary Institution Management System
**Approach:** Backend-First Rebuild with Full Modernization
**Spec Reference:** `docs/superpowers/specs/2026-04-02-tims-production-readiness-design.md`

---

## Why a Master Plan

The spec covers ~250 file changes across 10 logical phases. The `writing-plans` skill requires each plan to produce **working, testable software on its own**. A single 250-task plan would be unmanageable and impossible to resume after context loss. Instead, this master plan lists the phase plans in dependency order. Each phase plan:

- Is independently shippable (app still runs after each phase)
- Has its own atomic commits
- Passes its own tests before the next phase starts
- Lives in `docs/superpowers/plans/2026-04-16-phase-NN-<name>.md`

---

## Phase Sequence

| # | Phase | Plan File | Status | Est. Tasks |
|---|-------|-----------|--------|-----------|
| 1 | Foundation & Bug Fixes | `2026-04-16-phase-01-foundation.md` | ✅ Complete | ~20 |
| 2 | Backend Service Layer | `2026-04-16-phase-02-services.md` | ✅ Complete | ~18 |
| 3 | Backend Signals & Tasks | `2026-04-17-phase-03-signals-tasks.md` | ✅ Complete | ~10 |
| 4 | Backend Admin & Tests | `2026-04-16-phase-04-admin-tests.md` | ⏳ After Phase 3 | ~30 |
| 5 | Frontend TypeScript Migration | `2026-04-16-phase-05-typescript.md` | ⏳ After Phase 4 | ~25 |
| 6 | Frontend State & API Rewrite | `2026-04-16-phase-06-stores-api.md` | ⏳ After Phase 5 | ~22 |
| 7 | Frontend Page Completion | `2026-04-16-phase-07-pages.md` | ⏳ After Phase 6 | ~40 |
| 8 | Frontend Shared Components | `2026-04-16-phase-08-components.md` | ⏳ After Phase 7 | ~18 |
| 9 | Frontend Tests | `2026-04-16-phase-09-frontend-tests.md` | ⏳ After Phase 8 | ~20 |
| 10 | Production Config & CI/CD | `2026-04-16-phase-10-deploy.md` | ⏳ After Phase 9 | ~15 |
| 11 | Performance Optimization | `2026-04-16-phase-11-performance.md` | ⏳ After Phase 10 | ~12 |

**Total estimated tasks:** ~255 atomic steps across 11 phases.

---

## Dependency Rationale

```
Phase 1 (Foundation)
  └─→ Phase 2 (Service Layer) ─┐
                                ├─→ Phase 4 (Admin & Tests)
        Phase 3 (Signals/Tasks)─┘
                                 └─→ Phase 5 (TypeScript)
                                      └─→ Phase 6 (Stores/API)
                                           └─→ Phase 7 (Pages)
                                                └─→ Phase 8 (Components)
                                                     └─→ Phase 9 (FE Tests)
                                                          └─→ Phase 10 (Deploy)
                                                               └─→ Phase 11 (Perf)
```

**Why Phase 1 first:** Environment configuration, Celery, Redis, and security hardening are prerequisites for everything else. Can't run tests without pytest configured; can't run signals tests without Celery.

**Why backend before frontend:** Frontend types mirror backend serializers. TypeScript interfaces generated from backend shape need stable backend first.

**Why pages after stores:** Pages bind to Zustand stores. Building stores first means pages don't need rewrites mid-implementation.

---

## Phase 1 Deliverables (See detailed plan)

After Phase 1 completes, the app will have:
- ✅ All critical runtime bugs fixed (finance waivers, Library.jsx API call)
- ✅ Production-safe settings split (base/development/production)
- ✅ All secrets loaded from `.env` via python-decouple
- ✅ `requirements.txt` + `requirements-dev.txt` generated
- ✅ Celery + Redis operational with a test task
- ✅ Health check endpoint at `/api/health/`
- ✅ Git repository initialized with proper .gitignore, connected to GitHub origin
- ✅ Docker compose file for local dev (PostgreSQL + Redis)
- ✅ The app still runs exactly as before — no feature regressions

---

## Execution Protocol

For each phase:
1. Agent reads the phase plan
2. Executes tasks in order with atomic commits per task
3. Runs phase-level verification (tests, build, smoke test)
4. Commits & pushes to GitHub
5. Only then starts next phase plan

---

## Re-sync Points

After each phase, run these checks before proceeding:
- `python manage.py check --deploy` (production settings valid)
- `pytest` (all existing tests pass)
- `npm run build` (frontend still builds)
- Manual smoke: login, dashboard, one CRUD from each app
- `git status` clean; `git push` successful

If any check fails → fix before moving on. **No stacking broken state across phases.**
