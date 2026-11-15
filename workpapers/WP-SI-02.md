# WP-SI-02: Flaw Remediation

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | SI-2 Flaw Remediation |
| Origination | System-specific |
| Organization-defined parameter | Critical 15, High 30, Moderate 60, Low 90 days |
| Methods | Test |
| Evidence | E-05 (open vulnerability findings, 2026-09-29) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-09-29 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

Open flaws are fixed within the remediation window for their severity.

## Population

All 7 open findings in the scanner on 2026-09-29, exported during fieldwork with me watching.

## Results

| Finding | Component | Severity | Age (days) | Limit | Result |
|---|---|---|---|---|---|
| V-1031 | PDF rendering library 3.1.2 | Moderate | 85 | 60 | **Exception** |
| V-1044 | XML parsing library 2.9.0 | Moderate | 78 | 60 | **Exception** |
| V-1102 | OpenSSH client package (jump host) | Moderate | 12 | 60 | Within limit |
| V-1107 | Kernel package | High | 9 | 30 | Within limit |
| V-1088 | HTTP header disclosure | Low | 36 | 90 | Within limit |
| V-1095 | Timezone data package | Low | 26 | 90 | Within limit |
| V-1110 | Database version banner | Low | 2 | 90 | Within limit |

Re-performed by `src/control_tests.py` (`test_flaw_remediation`): 2 exceptions.

## Root cause (interview with the app team lead, 2026-10-01)

Both libraries are bundled in the application build, so OS patching does not update them. They
need an application release, and none was planned before release 2.4.

## Conclusion

**Conclusion:** Other than satisfied

Finding **AHR-2026-002** (Moderate). Recommendation: update the dependencies and fail CI builds
on findings past their deadline.
