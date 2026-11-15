# WP-CM-03: Configuration Change Control

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | CM-3 Configuration Change Control |
| Origination | System-specific |
| Methods | Examine, Test |
| Evidence | E-09 (Q3 2026 change records) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-10-02 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

Changes to the portal are approved and tested before they are implemented.

## Population and sample

- **Population:** 22 changes implemented in Q3 2026 (E-09). It arrived 2026-10-01, three days late.
- **Completeness check:** compared the change list with the release history in the deployment
  pipeline (releases 2.1, 2.2, 2.2.1, 2.3). All four releases appear.
- **Sample:** 10 (event-driven table, 11–50 items → 10).
- **Selection:** `python src/sampling.py evidence/E-09_change_records_2026-q3.csv --id-column change_id --seed 20260929`

## Results

| Change | Summary | Approved | Tested | Implemented | Exception |
|---|---|---|---|---|---|
| CHG-2026-0162 | Update WAF rule set | 2026-07-19 | Yes | 2026-07-21 | None |
| CHG-2026-0165 | Deploy release 2.2 | 2026-07-21 | Yes | 2026-07-25 | None |
| CHG-2026-0171 | Patch jump host | 2026-07-29 | Yes | 2026-07-30 | None |
| CHG-2026-0177 | Update log forwarding config | 2026-08-04 | Yes | 2026-08-05 | None |
| CHG-2026-0186 | Add SFTP source IP allowlist | 2026-08-12 | Yes | 2026-08-16 | None |
| CHG-2026-0189 | Update CIS hardening baseline | 2026-08-17 | Yes | 2026-08-19 | None |
| CHG-2026-0192 | Patch PostgreSQL minor version | 2026-08-18 | Yes | 2026-08-22 | None |
| CHG-2026-0195 | Deploy release 2.3 | 2026-08-22 | Yes | 2026-08-26 | None |
| CHG-2026-0198 | Resize app VM | 2026-08-28 | Yes | 2026-08-29 | None |
| CHG-2026-0207 | Patch jump host | 2026-09-04 | Yes | 2026-09-08 | None |

Re-performed by `src/control_tests.py` (`test_change_records`): 0 exceptions.

The one emergency change in the population (CHG-2026-0183, release 2.2.1 hotfix) was not
selected. I examined it separately: the ISSO approved it before deployment, which follows the
emergency change procedure.

## Conclusion

**Conclusion:** Satisfied
