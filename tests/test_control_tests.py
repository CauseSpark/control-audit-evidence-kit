from datetime import date

import pytest

import control_tests as ct
import sampling


# --- The Acme results line up with the SAR in rmf-ato-package-templates -------

@pytest.fixture(scope="module")
def results():
    return {r.control: r for r in ct.run_all()}


def test_ten_automated_tests(results):
    assert len(results) == 10


@pytest.mark.parametrize("control,expected", [
    ("AC-2", "Satisfied"), ("AC-2(3)", "Other than satisfied"), ("AC-6", "Satisfied"),
    ("AT-2", "Satisfied"), ("AU-6", "Other than satisfied"), ("CM-3", "Satisfied"),
    ("CM-6", "Other than satisfied"), ("RA-5", "Satisfied"), ("SI-2", "Other than satisfied"),
    ("SI-4", "Satisfied"),
])
def test_conclusions(results, control, expected):
    assert results[control].conclusion == expected


def test_inactive_accounts_match_sar(results):
    # SAR AHR-2026-001: six local and service accounts idle 41 to 97 days.
    r = results["AC-2(3)"]
    assert len(r.exceptions) == 6
    idle = sorted(int(x.split(": ")[1].split()[0]) for x in r.exceptions)
    assert (idle[0], idle[-1]) == (41, 97)
    assert any("breakglass-ahr" in o for o in r.observations)


def test_log_review_matches_sar(results):
    # SAR AHR-2026-004: weekly reviews recorded for 5 of the last 12 weeks.
    r = results["AU-6"]
    assert r.population == 12 and 12 - len(r.exceptions) == 5


def test_flaw_ages_match_sar(results):
    # SAR AHR-2026-002: two moderate flaws, 78 and 85 days old.
    ages = sorted(int(x.split(": ")[1].split()[0]) for x in results["SI-2"].exceptions)
    assert ages == [78, 85]


def test_tls_corrected_on_rescan(results):
    assert results["CM-6"].exceptions == ["TLSv1.0 offered", "TLSv1.1 offered"]
    rescan = ct.test_tls_configuration(ct.evidence_file("E-07").read_text(encoding="utf-8"))
    assert rescan.conclusion == "Satisfied"


def test_si4_late_triage_is_observation_not_exception(results):
    r = results["SI-4"]
    assert r.exceptions == []
    assert any("1 of 9" in o for o in r.observations)


# --- Each test catches what it should ---------------------------------------

def test_inactive_respects_limit_boundary():
    accts = [{"account": "a", "account_type": "service", "enabled": "Yes",
              "last_activity": "2026-08-26", "exception_ref": ""}]
    assert ct.test_inactive_accounts(accts, date(2026, 9, 30)).exceptions == []      # 35 days
    assert len(ct.test_inactive_accounts(accts, date(2026, 10, 1)).exceptions) == 1  # 36 days


def test_disabled_accounts_are_ignored():
    accts = [{"account": "a", "account_type": "service", "enabled": "No",
              "last_activity": "2025-01-01", "exception_ref": ""}]
    assert ct.test_inactive_accounts(accts, date(2026, 9, 30)).exceptions == []


def test_approval_after_grant_is_exception():
    grants = [{"grant_id": f"G-{i:03d}", "user": "u", "role": "HR Specialist",
               "granted_date": "2026-06-10", "ticket_id": f"T{i}"} for i in range(1, 6)]
    tickets = [{"ticket_id": f"T{i}", "user": "u", "role": "HR Specialist",
                "manager_approved_date": "2026-06-01",
                "isso_approved_date": "2026-06-12" if i == 3 else "2026-06-02"} for i in range(1, 6)]
    res = ct.test_access_approvals(grants, tickets, seed=1)
    assert res.tested == 5   # 10 or fewer items: test them all
    assert res.exceptions == ["G-003: ISSO approved 2026-06-12, after access on 2026-06-10"]


def test_missing_ticket_is_exception():
    grants = [{"grant_id": "G-001", "user": "u", "role": "r", "granted_date": "2026-06-10", "ticket_id": "T9"}]
    assert "not found" in ct.test_access_approvals(grants, [], seed=1).exceptions[0]


def test_flaw_at_exact_limit_passes():
    f = [{"finding_id": "V", "component": "c", "severity": "High", "first_detected": "2026-09-01", "status": "Open"}]
    assert ct.test_flaw_remediation(f, date(2026, 10, 1)).exceptions == []   # 30 days
    assert len(ct.test_flaw_remediation(f, date(2026, 10, 2)).exceptions) == 1


def test_offered_protocol_parser():
    text = "  TLSv1.0   not offered\n  TLSv1.1   offered\n  TLSv1.3   offered\n"
    assert ct.offered_protocols(text) == ["TLSv1.1", "TLSv1.3"]


def test_alert_rate_below_threshold_is_exception():
    alerts = [{"detection": "d", "alerts": "10", "tickets_opened": "10", "triaged_within_sla": "9"}]
    assert ct.test_alert_handling(alerts).exceptions   # 90% < 95%


def test_dual_access_is_exception():
    rows = [{"user": "x", "hr_app_role": "HR Administrator", "infrastructure_access": "Jump host"}]
    assert ct.test_least_privilege(rows).exceptions


# --- Sampling ---------------------------------------------------------------

@pytest.mark.parametrize("population,expected", [(0, 0), (1, 1), (10, 10), (11, 10), (50, 10),
                                                  (51, 25), (250, 25), (251, 40), (5000, 40)])
def test_population_bands(population, expected):
    assert sampling.sample_size_for_population(population) == expected


def test_frequency_sizes():
    assert sampling.sample_size_for_frequency("weekly") == 5
    assert sampling.sample_size_for_frequency("Quarterly", occurrences=1) == 1
    with pytest.raises(ValueError):
        sampling.sample_size_for_frequency("hourly")


def test_selection_is_reproducible_and_order_independent():
    items = [f"I-{i:03d}" for i in range(100)]
    a = sampling.select_sample(items, 10, seed=7)
    b = sampling.select_sample(list(reversed(items)), 10, seed=7)
    assert a == b and len(set(a)) == 10
    assert sampling.select_sample(items, 10, seed=8) != a


def test_selection_rejects_bad_input():
    with pytest.raises(ValueError):
        sampling.select_sample(["a", "b"], 3, seed=1)
    with pytest.raises(ValueError):
        sampling.select_sample(["a", "a", "b"], 2, seed=1)


def test_workpaper_samples_are_reproducible():
    grants = sampling.load_population(ct.evidence_file("E-02"), "grant_id")
    assert sampling.select_sample(grants, 10, ct.ACCESS_SAMPLE_SEED) == [
        "G-002", "G-004", "G-007", "G-009", "G-011", "G-012", "G-015", "G-018", "G-021", "G-022"]
