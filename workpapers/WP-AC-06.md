# WP-AC-06: Least Privilege (role separation)

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | AC-6 Least Privilege |
| Origination | System-specific |
| Methods | Examine, Test |
| Evidence | E-11 (role assignment export) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-09-30 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

System administrators have no HR application role, and HR staff have no infrastructure access
(SSP Section 3.2).

## Population

All 19 role holders on 2026-09-30: 12 HR Specialists, 3 HR Administrators, 4 System
Administrators (E-11, exported with me watching).

## Procedure performed

1. Checked every row for anyone holding both an HR application role and infrastructure access.
2. Compared the four system administrators with the local admin accounts in E-01 (adm-kpatel,
   adm-lchen, adm-rvasquez, adm-tbrooks).

## Results

| Check | Result |
|---|---|
| Users with both an HR role and infrastructure access | 0 |
| System administrators with an HR application role | 0 of 4 |
| HR staff with infrastructure access | 0 of 15 |

Re-performed by `src/control_tests.py` (`test_least_privilege`): 0 exceptions.

## Conclusion

**Conclusion:** Satisfied
