"""Re-perform the automated control tests against the evidence files.

Each function takes evidence (as rows or text) and returns a TestResult with the
population, the items tested, and any exceptions. The CLI runs every test against
the evidence folder and prints a summary that lines up with the workpapers.

    python src/control_tests.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from sampling import read_csv, sample_size_for_population, select_sample

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"

# Organization-defined parameters from the Acme HR Portal SSP (fictional).
INACTIVITY_LIMIT_DAYS = 35                      # AC-2(3)
REMEDIATION_DAYS = {"Critical": 15, "High": 30, "Moderate": 60, "Low": 90}   # SI-2
TRAINING_VALID_DAYS = 365                       # AT-2
TRIAGE_SLA_MIN_RATE = 0.95                      # SI-4, Internal Audit threshold
ACCESS_SAMPLE_SEED = 20260928                   # recorded in WP-AC-02
CHANGE_SAMPLE_SEED = 20260929                   # recorded in WP-CM-03


@dataclass
class TestResult:
    control: str
    test: str
    population: int
    tested: int
    exceptions: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def conclusion(self) -> str:
        return "Satisfied" if not self.exceptions else "Other than satisfied"


def d(value: str) -> date:
    return date.fromisoformat(value)


def evidence_file(evidence_id: str) -> Path:
    matches = sorted(EVIDENCE.glob(f"{evidence_id}_*"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one file for {evidence_id}, found {len(matches)}")
    return matches[0]


def draw_sample(rows: list[dict], id_column: str, seed: int) -> tuple[dict[str, dict], list[str]]:
    """Index the population by ID and draw the methodology sample from it."""
    by_id = {r[id_column]: r for r in rows}
    return by_id, select_sample(list(by_id), sample_size_for_population(len(rows)), seed)


# --- Tests ----------------------------------------------------------------

def test_access_approvals(grants: list[dict], tickets: list[dict], seed: int) -> TestResult:
    """AC-2: each sampled role grant has manager and ISSO approval on or before the grant date."""
    by_ticket = {t["ticket_id"]: t for t in tickets}
    by_grant, sample = draw_sample(grants, "grant_id", seed)
    res = TestResult("AC-2", "Role grants approved before access was given", len(grants), len(sample))
    for gid in sample:
        g = by_grant[gid]
        t = by_ticket.get(g["ticket_id"])
        if t is None:
            res.exceptions.append(f"{gid}: ticket {g['ticket_id']} not found")
            continue
        if t["user"] != g["user"] or t["role"] != g["role"]:
            res.exceptions.append(f"{gid}: ticket {t['ticket_id']} is for a different user or role")
        for col, who in (("manager_approved_date", "manager"), ("isso_approved_date", "ISSO")):
            if not t[col]:
                res.exceptions.append(f"{gid}: no {who} approval")
            elif d(t[col]) > d(g["granted_date"]):
                res.exceptions.append(f"{gid}: {who} approved {t[col]}, after access on {g['granted_date']}")
    return res


def test_inactive_accounts(accounts: list[dict], as_of: date,
                           limit: int = INACTIVITY_LIMIT_DAYS) -> TestResult:
    """AC-2(3): no enabled, non-exempt account is inactive longer than the limit."""
    enabled = [a for a in accounts if a["enabled"] == "Yes"]
    res = TestResult("AC-2(3)", f"Enabled accounts inactive more than {limit} days", len(accounts), len(enabled))
    for a in enabled:
        idle = (as_of - d(a["last_activity"])).days
        if idle <= limit:
            continue
        if a["exception_ref"]:
            res.observations.append(f"{a['account']}: {idle} days idle, exempt under {a['exception_ref']}")
        else:
            res.exceptions.append(f"{a['account']} ({a['account_type']}): {idle} days idle")
    return res


def test_least_privilege(assignments: list[dict]) -> TestResult:
    """AC-6: system administrators hold no HR application role; HR users have no infrastructure access."""
    res = TestResult("AC-6", "Separation of infrastructure and HR application roles", len(assignments), len(assignments))
    for a in assignments:
        if a["infrastructure_access"] != "None" and a["hr_app_role"] != "None":
            res.exceptions.append(f"{a['user']}: has both {a['hr_app_role']} and {a['infrastructure_access']} access")
    return res


def test_training(completions: list[dict], roster: list[dict], as_of: date,
                  valid_days: int = TRAINING_VALID_DAYS) -> TestResult:
    """AT-2: every portal HR or admin user passed awareness training in the last year."""
    done = {c["user"]: c for c in completions}
    res = TestResult("AT-2", "Annual awareness training current for all portal role holders", len(roster), len(roster))
    for person in roster:
        c = done.get(person["user"])
        if c is None:
            res.exceptions.append(f"{person['user']}: no training record")
        elif c["result"] != "Passed":
            res.exceptions.append(f"{person['user']}: result {c['result']}")
        elif (as_of - d(c["completed_date"])).days > valid_days:
            res.exceptions.append(f"{person['user']}: completed {c['completed_date']}, more than {valid_days} days ago")
    return res


def test_weekly_reviews(tickets: list[dict], first_week: date, weeks: int) -> TestResult:
    """AU-6: a completed review ticket exists for every week, finished within 7 days of the week start."""
    by_week = {t["week_start"]: t for t in tickets}
    res = TestResult("AU-6", "Weekly portal log review documented", weeks, weeks)
    for i in range(weeks):
        wk = first_week + timedelta(weeks=i)
        t = by_week.get(wk.isoformat())
        if t is None:
            res.exceptions.append(f"week of {wk}: no review recorded")
        elif (d(t["completed_date"]) - wk).days > 6:
            res.exceptions.append(f"week of {wk}: review completed late on {t['completed_date']}")
    return res


def test_change_records(changes: list[dict], seed: int) -> TestResult:
    """CM-3: each sampled change was approved and tested before it was implemented."""
    by_id, sample = draw_sample(changes, "change_id", seed)
    res = TestResult("CM-3", "Changes approved and tested before implementation", len(changes), len(sample))
    for cid in sample:
        c = by_id[cid]
        if not c["approved_date"] or d(c["approved_date"]) > d(c["implemented_date"]):
            res.exceptions.append(f"{cid}: not approved before implementation")
        if c["tested_before_release"] != "Yes":
            res.exceptions.append(f"{cid}: not tested before release")
    return res


LEGACY = ("SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1")


def offered_protocols(scan_text: str) -> list[str]:
    found = []
    for line in scan_text.splitlines():
        m = re.match(r"\s*(SSLv2|SSLv3|TLSv1\.[0-3])\s+(offered|not offered)\s*$", line)
        if m and m.group(2) == "offered":
            found.append(m.group(1))
    return found


def test_tls_configuration(scan_text: str) -> TestResult:
    """CM-6: the load balancer offers nothing below TLS 1.2."""
    offered = offered_protocols(scan_text)
    res = TestResult("CM-6", "No protocol below TLS 1.2 offered", len(LEGACY) + 2, len(LEGACY) + 2)
    res.exceptions = [f"{p} offered" for p in offered if p in LEGACY]
    return res


def test_scan_coverage(runs: list[dict], first_scan: date, last_scan: date) -> TestResult:
    """RA-5: a successful credentialed scan of every asset ran each week."""
    by_date = {r["scan_date"]: r for r in runs}
    expected = []
    cur = first_scan
    while cur <= last_scan:
        expected.append(cur)
        cur += timedelta(weeks=1)
    res = TestResult("RA-5", "Weekly credentialed scan of all assets", len(expected), len(expected))
    for day in expected:
        r = by_date.get(day.isoformat())
        if r is None:
            res.exceptions.append(f"{day}: no scan")
            continue
        scanned, total = (int(x) for x in r["assets_scanned"].split("/"))
        if r["status"] != "Success" or r["scan_type"] != "Credentialed" or scanned < total:
            res.exceptions.append(f"{day}: {r['status']}, {r['scan_type']}, {r['assets_scanned']} assets")
    return res


def test_flaw_remediation(findings: list[dict], as_of: date,
                          windows: dict[str, int] = REMEDIATION_DAYS) -> TestResult:
    """SI-2: no open flaw is older than its severity's remediation window."""
    res = TestResult("SI-2", "Open flaws within remediation windows", len(findings), len(findings))
    for f in findings:
        if f["status"] != "Open":
            continue
        age = (as_of - d(f["first_detected"])).days
        limit = windows[f["severity"]]
        if age > limit:
            res.exceptions.append(f"{f['finding_id']} {f['severity']}: {age} days old (limit {limit}): {f['component']}")
    return res


def test_alert_handling(alerts: list[dict], min_rate: float = TRIAGE_SLA_MIN_RATE) -> TestResult:
    """SI-4: every alert produced a ticket and triage met the SLA at the required rate."""
    total = sum(int(a["alerts"]) for a in alerts)
    on_time = sum(int(a["triaged_within_sla"]) for a in alerts)
    res = TestResult("SI-4", "Alerts ticketed and triaged on time", total, total)
    for a in alerts:
        if int(a["tickets_opened"]) < int(a["alerts"]):
            res.exceptions.append(f"{a['detection']}: {a['alerts']} alerts but {a['tickets_opened']} tickets")
        late = int(a["alerts"]) - int(a["triaged_within_sla"])
        if late:
            res.observations.append(f"{a['detection']}: {late} of {a['alerts']} triaged after the SLA")
    rate = on_time / total if total else 1.0
    if rate < min_rate:
        res.exceptions.append(f"triage on time {rate:.0%}, below the {min_rate:.0%} threshold")
    else:
        res.observations.append(f"triage on time {on_time}/{total} ({rate:.0%}), meets the {min_rate:.0%} threshold")
    return res


# --- Runner ---------------------------------------------------------------

def run_all() -> list[TestResult]:
    e = evidence_file
    roster = read_csv(e("E-11"))
    return [
        test_access_approvals(read_csv(e("E-02")), read_csv(e("E-03")), ACCESS_SAMPLE_SEED),
        test_inactive_accounts(read_csv(e("E-01")), as_of=date(2026, 9, 30)),
        test_least_privilege(roster),
        test_training(read_csv(e("E-10")), roster, as_of=date(2026, 9, 30)),
        test_weekly_reviews(read_csv(e("E-04")), first_week=date(2026, 7, 6), weeks=12),
        test_change_records(read_csv(e("E-09")), CHANGE_SAMPLE_SEED),
        test_tls_configuration(e("E-06").read_text(encoding="utf-8")),
        test_scan_coverage(read_csv(e("E-12")), date(2026, 7, 5), date(2026, 9, 27)),
        test_flaw_remediation(read_csv(e("E-05")), as_of=date(2026, 9, 29)),
        test_alert_handling(read_csv(e("E-13"))),
    ]


def main() -> int:
    results = run_all()
    print(f"{'Control':<8} {'Result':<21} {'Tested':>9}  Test")
    for r in results:
        print(f"{r.control:<8} {r.conclusion:<21} {r.tested:>4}/{r.population:<4}  {r.test}")
        for x in r.exceptions:
            print(f"{'':<8}   exception: {x}")
        for o in r.observations:
            print(f"{'':<8}   note: {o}")
    retest = test_tls_configuration(evidence_file("E-07").read_text(encoding="utf-8"))
    print(f"\nCM-6 retest on 2026-10-07 rescan (E-07): {retest.conclusion}")
    failed = sum(1 for r in results if r.exceptions)
    print(f"\n{len(results)} automated tests, {failed} with exceptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
