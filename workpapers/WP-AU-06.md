# WP-AU-06: Audit Record Review, Analysis, and Reporting

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | AU-6 Audit Record Review, Analysis, and Reporting |
| Origination | Hybrid (SOC monitors centrally; the ISSO reviews portal-specific events) |
| Methods | Examine, Interview |
| Evidence | E-04 (weekly review tickets) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-09-30 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

The ISSO reviews portal-specific audit logs every week and records each review (SSP Section 5, AU-6).

## Population

All 12 weeks from the week of 2026-07-06 through the week of 2026-09-21. A weekly control
would normally be sampled at 5, but the full population was small and easy to get, so I tested all 12.

## Procedure performed

1. Listed the 12 weeks and looked for a completed review ticket for each one in E-04.
2. Checked that each ticket was completed within the same week and had the checklist attached.
3. Interviewed Sam Okafor, ISSO, on 2026-09-30.

## Results

| Week of | Ticket | Completed | Result |
|---|---|---|---|
| 2026-07-06 | TD-40310 | 2026-07-08 | Documented |
| 2026-07-13 | none | | **Missing** |
| 2026-07-20 | TD-40655 | 2026-07-21 | Documented |
| 2026-07-27 | none | | **Missing** |
| 2026-08-03 | none | | **Missing** |
| 2026-08-10 | TD-41190 | 2026-08-12 | Documented |
| 2026-08-17 | none | | **Missing** |
| 2026-08-24 | none | | **Missing** |
| 2026-08-31 | TD-41702 | 2026-09-02 | Documented |
| 2026-09-07 | none | | **Missing** |
| 2026-09-14 | none | | **Missing** |
| 2026-09-21 | TD-42230 | 2026-09-23 | Documented |

**5 of 12 weeks documented.** Re-performed by `src/control_tests.py` (`test_weekly_reviews`).

## Interview note

The ISSO said reviews were done most weeks but were recorded only when something looked
suspicious. Without records, Internal Audit cannot confirm that the missing reviews happened.
SOC central alerting was active the whole period (see WP-SI-04), which limits the impact.

## Conclusion

**Conclusion:** Other than satisfied

Finding **AHR-2026-004** (Low). Recommendation: use a recurring review ticket with a checklist so
every weekly review leaves a record.
