# WP-RA-05: Vulnerability Monitoring and Scanning

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | RA-5 Vulnerability Monitoring and Scanning |
| Origination | System-specific |
| Methods | Examine |
| Evidence | E-12 (authenticated scan run history, Q3 2026) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-09-30 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

Every asset in the boundary gets a successful credentialed scan each week (ConMon plan).

## Population

All 13 weekly scans from 2026-07-05 to 2026-09-27.

## Results

| Check | Result |
|---|---|
| Weeks with a scan | 13 of 13 |
| Scans run credentialed | 13 of 13 |
| Scans reaching all 8 assets | 13 of 13 |

Re-performed by `src/control_tests.py` (`test_scan_coverage`): 0 exceptions.

Scanning is working. The findings are in fixing what the scans find, which is covered in
WP-SI-02.

## Conclusion

**Conclusion:** Satisfied
