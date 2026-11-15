# WP-AC-02: Account Management (role grant approvals)

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | AC-2 Account Management |
| Origination | System-specific |
| Methods | Examine, Test |
| Evidence | E-02 (role grants), E-03 (access request tickets) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-10-02 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

HR Specialist and HR Administrator roles are granted only after the user's manager and the
ISSO approve a documented request (SSP Section 5, AC-2).

## Population and sample

- **Population:** 25 role grants from 2026-05-01 to 2026-09-30 (E-02), pulled from the portal
  admin console while I watched.
- **Completeness check:** compared the count with the role assignment export (E-11). All 15
  current HR role holders appear in the population. The other 10 grants are pilot testers whose
  roles were removed later.
- **Sample:** 10 grants, per the event-driven table in `docs/sampling_guide.md` (11–50 items → 10).
- **Selection:** `python src/sampling.py evidence/E-02_hr_role_grants_2026-05-01_to_2026-09-30.csv --id-column grant_id --seed 20260928`

## Procedure performed

1. For each sampled grant, found the ticket in E-03.
2. Confirmed the ticket names the same user and role.
3. Confirmed that both the manager and the ISSO approved the ticket on or before the grant date.

## Results

| Grant | User | Role | Ticket | Manager approved | ISSO approved | Granted | Exception |
|---|---|---|---|---|---|---|---|
| G-002 | Gray Grant | HR Specialist | TD-41207 | 2026-05-11 | 2026-05-12 | 2026-05-17 | None |
| G-004 | Indigo Ito | HR Specialist | TD-41221 | 2026-05-23 | 2026-05-25 | 2026-05-30 | None |
| G-007 | Logan Lund | HR Specialist | TD-41242 | 2026-06-12 | 2026-06-12 | 2026-06-17 | None |
| G-009 | Finley Flores | HR Specialist | TD-41256 | 2026-06-22 | 2026-06-24 | 2026-06-29 | None |
| G-011 | Vale Vance | HR Specialist | TD-41270 | 2026-07-05 | 2026-07-06 | 2026-07-11 | None |
| G-012 | Taylor Tran | HR Specialist | TD-41277 | 2026-07-14 | 2026-07-15 | 2026-07-17 | None |
| G-015 | Jules Jensen | HR Specialist | TD-41298 | 2026-07-27 | 2026-07-28 | 2026-07-31 | None |
| G-018 | Casey Cortez | HR Specialist | TD-41319 | 2026-08-08 | 2026-08-09 | 2026-08-13 | None |
| G-021 | Noel Nakamura | HR Administrator | TD-41340 | 2026-08-19 | 2026-08-19 | 2026-08-26 | None |
| G-022 | Xen Xu | HR Administrator | TD-41347 | 2026-08-29 | 2026-08-29 | 2026-09-01 | None |

Re-performed by `src/control_tests.py` (`test_access_approvals`): 0 exceptions.

## Conclusion

**Conclusion:** Satisfied

Every sampled grant was approved by both the manager and the ISSO before access was given.
