import csv
import shutil
from datetime import date
from pathlib import Path

import pytest

import evidence_check as ec

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def kit(tmp_path):
    """A writable copy of the repo's assessment files."""
    for d in ("procedures", "pbc", "evidence", "workpapers"):
        shutil.copytree(ROOT / d, tmp_path / d)
    return tmp_path


def edit_csv(path, fn):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        fn(r)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def test_repo_passes():
    rep = ec.check()
    assert rep.ok, rep.problems


def test_final_follow_ups_are_only_late_receipts():
    rep = ec.check()
    assert len(rep.warnings) == 5
    assert all("late" in w for w in rep.warnings)


def test_mid_fieldwork_shows_open_and_overdue():
    rep = ec.check(as_of=date(2026, 9, 29))
    states = [r["state"] for r in rep.pbc_rows]
    assert states.count("Open") == 8
    assert any("PBC-07: overdue by 1 day" in w for w in rep.warnings)
    assert any("AC-2(3): waiting on E-01" in w for w in rep.warnings)


def test_every_plan_control_has_a_workpaper():
    plan = ec.read_csv(ROOT / "procedures" / "assessment_plan.csv")
    assert len(plan) == 12
    for p in plan:
        assert (ROOT / "workpapers" / f"{p['workpaper']}.md").exists()


def test_findings_match_sar():
    plan = ec.read_csv(ROOT / "procedures" / "assessment_plan.csv")
    findings = {p["control_id"]: p["finding_id"] for p in plan if p["finding_id"]}
    assert findings == {"AC-2(3)": "AHR-2026-001", "SI-2": "AHR-2026-002", "CP-4": "AHR-2026-003",
                        "AU-6": "AHR-2026-004", "CM-6": "AHR-2026-005"}


def test_tampered_evidence_is_caught(kit):
    f = kit / "evidence" / "E-04_audit_review_tickets_2026-07-06_to_2026-09-27.csv"
    f.write_text(f.read_text() + "2026-07-13,TD-99999,2026-07-14,Sam Okafor,Yes\n")
    rep = ec.check(kit)
    assert any("E-04: SHA-256 does not match" in p for p in rep.problems)


def test_missing_file_is_caught(kit):
    (kit / "evidence" / "E-13_soc_alert_summary_2026-q3.csv").unlink()
    assert any("E-13: file" in p for p in ec.check(kit).problems)


def test_stale_export_is_caught(kit):
    edit_csv(kit / "pbc" / "evidence_index.csv",
             lambda r: r.update(generated_date="2026-08-01") if r["evidence_id"] == "E-01" else None)
    assert any("E-01: export generated 2026-08-01" in p for p in ec.check(kit).problems)


def test_satisfied_without_available_evidence_is_caught(kit):
    def flip(r):
        if r["control_id"] == "CP-4":
            r.update(result="Satisfied", finding_id="")
    edit_csv(kit / "procedures" / "assessment_plan.csv", flip)
    problems = ec.check(kit).problems
    assert any("CP-4: concluded Satisfied but required evidence was not available" in p for p in problems)
    assert any("CP-4: workpaper concludes 'Other than satisfied'" in p for p in problems)


def test_other_than_satisfied_needs_finding(kit):
    edit_csv(kit / "procedures" / "assessment_plan.csv",
             lambda r: r.update(finding_id="") if r["control_id"] == "SI-2" else None)
    assert any("SI-2: Other than satisfied needs a finding ID" in p for p in ec.check(kit).problems)


def test_untracked_client_evidence_is_caught(kit):
    edit_csv(kit / "pbc" / "evidence_request_list.csv",
             lambda r: r.update(evidence_id="") if r["request_id"] == "PBC-11" else None)
    assert any("E-13: provided by SOC Manager but no evidence request" in p for p in ec.check(kit).problems)


def test_workpaper_must_cite_its_evidence(kit):
    wp = kit / "workpapers" / "WP-RA-05.md"
    wp.write_text(wp.read_text().replace("E-12", "the scan history"))
    assert any("RA-5: workpaper does not cite E-12" in p for p in ec.check(kit).problems)


def test_write_hashes_fills_blanks_only(kit):
    edit_csv(kit / "pbc" / "evidence_index.csv",
             lambda r: r.update(sha256="") if r["evidence_id"] == "E-05" else None)
    assert ec.write_hashes(kit) == 1
    assert ec.check(kit).ok


def test_cli_exit_codes(capsys):
    assert ec.main([]) == 0
    assert "Problems: none" in capsys.readouterr().out
