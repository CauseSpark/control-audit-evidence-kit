# WP-CP-04: Contingency Plan Testing

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | CP-4 Contingency Plan Testing |
| Origination | System-specific |
| Methods | Examine, Interview |
| Evidence | E-08 (system owner response to PBC-08) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-09-30 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

The contingency plan has been tested and the results recorded.

## Procedure performed

1. Requested the most recent test or exercise report (PBC-08).
2. The system owner answered in writing that no test exists (E-08).
3. Interviewed Dana Ruiz, System Owner, on 2026-09-30 to confirm and to ask about plans.

## Results

| Check | Result |
|---|---|
| Contingency plan approved | Yes, v1.0 on 2026-08-14 |
| Test or tabletop exercise performed | **No** |
| Database restore performed from backups | **No** |
| Test scheduled | Tabletop January 2027, restore test February 2027 |

PBC-08 is marked **Not Available**. `src/evidence_check.py` blocks a Satisfied conclusion when
required evidence is not available.

## Conclusion

**Conclusion:** Other than satisfied

Finding **AHR-2026-003** (Low; availability is categorized LOW). Recommendation: run the
tabletop exercise and a database restore test and record the results.
