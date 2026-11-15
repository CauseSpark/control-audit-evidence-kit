# WP-CM-06: Configuration Settings (TLS)

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | CM-6 Configuration Settings |
| Origination | System-specific |
| Methods | Test |
| Evidence | E-06 (TLS scan, 2026-09-30), E-07 (rescan, 2026-10-07) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-10-07 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

The load balancer offers only TLS 1.2 or higher, as the SSP requires (data flows 1 and 2).

## Procedure performed

I ran the scans from the Internal Audit workstation. Evidence the assessor produces directly is
the most reliable kind, because the system owner never handles it.

## Results

| Scan | TLS 1.0 | TLS 1.1 | TLS 1.2 | TLS 1.3 | Result |
|---|---|---|---|---|---|
| E-06, 2026-09-30 | offered | offered | offered | offered | **Exception** |
| E-07, 2026-10-07 (after CHG-2026-0219) | not offered | not offered | offered | offered | Corrected |

Re-performed by `src/control_tests.py` (`test_tls_configuration`) on both files.

## Conclusion

**Conclusion:** Other than satisfied

The control was not operating as described when the assessment started. Finding
**AHR-2026-005** (Low), **corrected during the assessment** and verified by the 2026-10-07
rescan. It is reported in the SAR so the AO sees it happened. No POA&M item is needed.
