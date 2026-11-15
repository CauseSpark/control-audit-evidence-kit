# control-audit-evidence-kit

[![tests](https://github.com/CauseSpark/control-audit-evidence-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/CauseSpark/control-audit-evidence-kit/actions/workflows/tests.yml)

The evidence trail behind a security control assessment: an assessment plan, an evidence
request (PBC) list, hashed evidence files, reproducible samples, automated control tests, and
one workpaper per control. A checker ties it all together and fails if any conclusion isn't
backed by evidence.

It reconstructs how the five findings in the
[Acme HR Portal SAR](https://github.com/CauseSpark/rmf-ato-package-templates/blob/main/examples/acme-hr-portal/sar.md)
were reached. Running the tests against the evidence reproduces each finding exactly.

> **Personal study material.** This is not an official NIST or DoD product and does not
> represent a real assessment. Acme Defense Fabrication, the HR Portal, every person, account,
> ticket, and scan result are fictional. No real system data is included.

## Purpose

A finding is only as strong as the evidence behind it. Auditors and assessors spend most of their
time on things a framework doesn't spell out: asking for the right evidence, checking it's
complete and unaltered, picking a fair sample, and writing down enough that someone else could
re-perform the test. This repo practices those steps on one system, end to end.

## Version referenced (checked November 2026)

| Source | Version |
|---|---|
| [NIST SP 800-53A Rev 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) | January 2022, Release 5.2.0 (August 2025). Examine, interview, and test methods, and assessment objectives |
| [NIST SP 800-53 Rev 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Release 5.2.0. The controls being assessed |

## Quick start

```bash
git clone https://github.com/CauseSpark/control-audit-evidence-kit.git
cd control-audit-evidence-kit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python src/control_tests.py                        # re-perform the automated control tests
python src/evidence_check.py                       # check the evidence trail (final status)
python src/evidence_check.py --as-of 2026-09-29    # PBC status partway through fieldwork
pytest
```

Sample output from `control_tests.py`:

```
Control  Result                   Tested  Test
AC-2     Satisfied               10/25    Role grants approved before access was given
AC-2(3)  Other than satisfied    18/19    Enabled accounts inactive more than 35 days
           exception: svc-ahr-db-migrate (service): 64 days idle
           ...
           note: breakglass-ahr: 168 days idle, exempt under EX-2026-01
AU-6     Other than satisfied    12/12    Weekly portal log review documented
           exception: week of 2026-07-13: no review recorded
           ...
SI-2     Other than satisfied     7/7     Open flaws within remediation windows
           exception: V-1031 Moderate: 85 days old (limit 60): app VMs: PDF rendering library 3.1.2
           exception: V-1044 Moderate: 78 days old (limit 60): app VMs: XML parsing library 2.9.0
SI-4     Satisfied               32/32    Alerts ticketed and triaged on time
           note: triage on time 31/32 (97%), meets the 95% threshold

CM-6 retest on 2026-10-07 rescan (E-07): Satisfied
```

## Controls assessed

A representative 12 of the system's controls, picked to cover every method, all three
origination types, both sample types, and both conclusions.

| Control | Method | Coverage | Result | Finding |
|---|---|---|---|---|
| AC-2 Account Management | Examine, Test | Sample 10 of 25 | Satisfied | |
| AC-2(3) Disable Accounts | Test | All 19 accounts | **Other than satisfied** | AHR-2026-001 |
| AC-6 Least Privilege | Examine, Test | All 19 role holders | Satisfied | |
| AT-2 Literacy Training | Examine | All 19 role holders | Satisfied | |
| AU-6 Audit Record Review | Examine, Interview | All 12 weeks | **Other than satisfied** | AHR-2026-004 |
| CM-3 Change Control | Examine, Test | Sample 10 of 22 | Satisfied | |
| CM-6 Configuration Settings | Test | Assessor-run scan | **Other than satisfied** (corrected) | AHR-2026-005 |
| CP-4 Contingency Plan Testing | Examine, Interview | Single plan | **Other than satisfied** | AHR-2026-003 |
| IA-2(1) MFA (inherited) | Examine | Provider authorization | Satisfied | |
| RA-5 Vulnerability Scanning | Examine | All 13 weeks | Satisfied | |
| SI-2 Flaw Remediation | Test | All 7 open flaws | **Other than satisfied** | AHR-2026-002 |
| SI-4 System Monitoring | Examine, Interview | All 32 alerts | Satisfied (one observation) | |

## What's in the repo

| Path | What it is |
|---|---|
| `procedures/assessment_plan.csv` | Each control's objective, methods, assessment objects, evidence, coverage, and result |
| `pbc/evidence_request_list.csv` | The 12 evidence requests: owner, due date, received date, status, whether the assessor watched |
| `pbc/evidence_index.csv` | All 14 evidence items with type, source, date, provider, and SHA-256 hash |
| `evidence/` | The fictional evidence: account lists, tickets, scans, change records, memos |
| `workpapers/` | One workpaper per control, plus `TEMPLATE.md` |
| `src/control_tests.py` | Ten automated re-performance tests |
| `src/sampling.py` | Methodology sample sizes and seeded, reproducible selection |
| `src/evidence_check.py` | Integrity, freshness, completeness, and timeliness checks across all of the above |
| `docs/audit_workflow.md` | Plan, request, collect, test, conclude, report |
| `docs/sampling_guide.md` | When and how much to sample |
| `tests/` | 51 pytest cases, including tamper, staleness, and unsupported-conclusion cases |

## What the checker catches

| Problem | Example |
|---|---|
| Evidence changed after receipt | Someone adds a missing review week to E-04 → SHA-256 mismatch |
| Stale evidence | An account export generated two months before fieldwork |
| Unsupported conclusion | CP-4 marked Satisfied when the test report was Not Available |
| Plan and workpaper disagree | Plan says Satisfied, workpaper says Other than satisfied |
| Missing finding | Other than satisfied with no finding ID |
| Untracked client evidence | A file from the SOC with no matching request |
| Overdue requests | `--as-of` shows which owners are late during fieldwork |

## What this demonstrates

- **Assessment method:** SP 800-53A examine, interview, and test, with inherited controls handled
  by confirming the provider's authorization instead of retesting it
- **Evidence handling:** watched queries, assessor-run scans, hashing on receipt, and freshness rules
- **Sampling:** a documented methodology, completeness checks on each population, and seeded selection
- **Judgment:** the difference between an exception and an observation, and when a result needs a finding
- **Traceability:** evidence → test → workpaper → finding → SAR → POA&M, checked in CI

## Related repos

Part 2 of a four-repo series on the same fictional system:

1. [risk-assessment-800-30](https://github.com/CauseSpark/risk-assessment-800-30): what could go wrong and how bad it is
2. **control-audit-evidence-kit** (this repo): how the controls were tested and what evidence backs each result
3. [policy-and-poam-program](https://github.com/CauseSpark/policy-and-poam-program): the policies and the POA&M tracker that drives the fixes
4. [security-risk-briefings](https://github.com/CauseSpark/security-risk-briefings): how it's explained to leadership

## Disclaimer

This repository is personal study material created for learning and portfolio purposes:

- It is **not** affiliated with or endorsed by NIST, the DoD, or any employer or client.
- It does **not** represent a real assessment, audit opinion, or compliance advice.
- All names, accounts, tickets, scans, and results are fictional.

Control objectives are my own short paraphrases. Use SP 800-53A for the official assessment procedures.

## License

[MIT](LICENSE) © 2026 Peyton Seay
