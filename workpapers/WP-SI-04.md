# WP-SI-04: System Monitoring

> FICTIONAL workpaper. Acme Defense Fabrication and every person named are invented.

| Field | Value |
|---|---|
| Control | SI-4 System Monitoring |
| Origination | Hybrid (SOC platform and detections are enterprise; tuning for the portal is system-specific) |
| Methods | Examine, Interview |
| Evidence | E-13 (Q3 2026 SOC alert summary) |
| Prepared by / date | Jordan Pike, Lead Assessor, 2026-10-03 |
| Reviewed by / date | Rowan Ellis, Internal Audit Manager, 2026-10-12 |

## Objective

SOC detections that cover the portal produce tickets, and at least 95% of alerts are triaged
within the SOC's SLA.

## Population

All 32 alerts from five detections in Q3 2026. Each detection is mapped to the 800-53 controls it
supports, the same way my
[nist-800-53-control-mapping](https://github.com/CauseSpark/nist-800-53-control-mapping) repo maps
Splunk searches. The portal runs on Linux, so these detections watch Linux authentication and
audit events rather than Windows event codes.

## Results

| Detection | Controls supported | Alerts | Tickets | Triaged within SLA |
|---|---|---|---|---|
| Repeated SSH authentication failures on jump host | AC-7, AU-6, SI-4 | 14 | 14 | 14 |
| New sudoers entry or admin group change | AC-2(4), AC-6(9), SI-4 | 6 | 6 | 6 |
| Audit daemon stopped or log file cleared | AU-9, AU-6, SI-4 | 2 | 2 | 2 |
| Off-hours privileged session on jump host | AC-2(12), AC-6(9), AU-6 | 9 | 9 | 8 |
| Outbound transfer over 1 GB from app VM | SI-4, SC-7 | 1 | 1 | 1 |
| **Total** | | **32** | **32** | **31 (97%)** |

Re-performed by `src/control_tests.py` (`test_alert_handling`).

## Interview note (SOC Manager, 2026-10-03)

The late triage was an off-hours alert raised during a holiday weekend. On-call coverage has
since been added to the holiday schedule. All 32 alerts turned out to be authorized activity.

## Conclusion

**Conclusion:** Satisfied

One alert was triaged late. That is recorded as an **observation**, not a finding, because the
on-time rate (97%) meets the 95% threshold.
