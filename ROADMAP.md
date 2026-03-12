# DataLint Roadmap - Version 1.0

## Project Overview
- **Project Name**: DataLint
- **Type**: Python CLI tool for ML data validation
- **Core Value**: Automated data validation that learns from clean datasets to prevent ML training failures
- **Target Users**: Data Scientists, ML Engineers, DevOps

---

## Current Status (March 2026)

### Completed Phases
| Phase | Status | Completion Date |
|-------|--------|-----------------|
| Phase 1: Core Validation Engine | DONE | 2026-01 |
| Phase 2: Learning System | DONE | 2026-02 |

### Current Progress: 10% (Mom Test Phase)

---

## Roadmap (Minimum 4 Months)

### Phase 3: Mom Test & Validation (Weeks 1-4)
**Duration**: March 2026 (4 weeks)
**Objective**: Validate product-market fit through Mom Test

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1 | Mom Test Interviews | 5+ user interviews documented |
| 2 | Decision | GO/NO-GO/Pivot decision |
| 3 | Marketing Validation | Landing page, 3+ sources researched |
| 4 | Iteration | Product adjustments based on feedback |

**Success Criteria**:
- 3+ spontaneous mentions of data quality problems
- 2+ solution seekers (users asking for the product)
- Decision.md with GO/NO-GO justification

---

### Phase 4: Core Features Expansion (Weeks 5-8)
**Duration**: April 2026 (4 weeks)
**Objective**: Complete MVP with all core features

| Week | Feature | Deliverables |
|------|---------|--------------|
| 5 | HTML Reports | Report generation in HTML format |
| 6 | JSON Export | Full JSON output for CI/CD |
| 7 | GitHub Actions | GitHub Actions integration |
| 8 | Testing & Polish | 60%+ coverage, all tests passing |

**Success Criteria**:
- HTML report generation working
- JSON output validated
- GitHub Actions workflow example
- 60% test coverage minimum

---

### Phase 5: Distribution & Launch (Weeks 9-12)
**Duration**: May 2026 (4 weeks)
**Objective**: Launch to market and gather feedback

| Week | Activity | Deliverables |
|------|----------|--------------|
| 9 | PyPI Release | Package published on PyPI |
| 10 | Documentation | Full API docs, README improvements |
| 11 | Community | Reddit/HackerNews posts, feedback collection |
| 12 | Launch | v1.0.0 release, release notes |

**Success Criteria**:
- 100+ PyPI downloads
- 3+ blog posts or social mentions
- 10+ GitHub stars

---

### Phase 6: Enterprise Features (Weeks 13-16)
**Duration**: June 2026 (4 weeks)
**Objective**: Add enterprise-grade features

| Week | Feature | Deliverables |
|------|---------|--------------|
| 13 | Web Dashboard | Basic web UI for report viewing |
| 14 | Team Collaboration | Multi-user support, sharing |
| 15 | API Server | REST API for integration |
| 16 | Security | Authentication, encryption |

**Success Criteria**:
- Web dashboard running
- API with authentication
- Enterprise pricing defined

---

## Anti-Goals (What NOT to Build)
- No cloud hosting (keep it local-first)
- No database requirement (file-based only)
- No enterprise SSO for v1.0
- No real-time streaming validation

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low user interest | Medium | High | Pivot to general data tools |
| Competition | High | Medium | Focus on ML-specific features |
| Technical debt | High | Medium | 60% test coverage enforced |
| Scope creep | High | High | Strict phase gates |

---

## Resources Required
- Python 3.10+
- pytest, pytest-cov
- GitHub Actions (free tier)
- PyPI account (free)

---

## Next Step
**Immediate**: Complete Mom Test (Phase 3, Week 1-2)
- Create mom_test_script.md with EN/FR questions
- Conduct 5 interviews
- Document in mom_test_results.md
- Create decision.md with GO/NO-GO