"""Check the evidence trail behind an assessment and report its status.

Ties together four files:

* procedures/assessment_plan.csv  what each control needs and the conclusion reached
* pbc/evidence_request_list.csv   what was requested, from whom, and when it arrived
* pbc/evidence_index.csv          every evidence file, its date, type, and SHA-256 hash
* evidence/ and workpapers/       the files themselves

    python src/evidence_check.py                       # final status
    python src/evidence_check.py --as-of 2026-09-29    # status partway through fieldwork
    python src/evidence_check.py --write-hashes        # record hashes for newly received files

Exit code 1 means at least one integrity or completeness problem.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDWORK_START = date(2026, 9, 28)
FIELDWORK_END = date(2026, 10, 9)

# How old evidence may be, by type, measured back from the start of fieldwork.
# Documents (signed letters, approved plans) have no age limit here; their currency is
# judged in the workpaper.
FRESHNESS_DAYS = {"export": 7, "report": 30, "document": None}
RESULTS = {"Satisfied", "Other than satisfied"}
PBC_STATUSES = {"Open", "Received", "Not Available"}
AUDITOR = "Internal Audit"


@dataclass
class Report:
    as_of: date
    problems: list[str] = field(default_factory=list)     # integrity or completeness failures
    warnings: list[str] = field(default_factory=list)     # timeliness and follow-ups
    pbc_rows: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_ids(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def pbc_state(row: dict, as_of: date) -> str:
    """Status of a request as it stood on the as_of date."""
    received = date.fromisoformat(row["received_date"]) if row["received_date"] else None
    if received and received <= as_of:
        return row["status"]
    return "Open"


def check(root: Path = ROOT, as_of: date = FIELDWORK_END) -> Report:
    plan = read_csv(root / "procedures" / "assessment_plan.csv")
    pbc = read_csv(root / "pbc" / "evidence_request_list.csv")
    index = {r["evidence_id"]: r for r in read_csv(root / "pbc" / "evidence_index.csv")}
    rep = Report(as_of=as_of)
    pbc_by_ev = {r["evidence_id"]: r for r in pbc}

    # 1. Evidence index: files exist, hashes match, dates are fresh enough.
    for ev_id, ev in index.items():
        path = root / "evidence" / ev["file"]
        if not path.exists():
            rep.problems.append(f"{ev_id}: file {ev['file']} is missing")
            continue
        if not ev["file"].startswith(f"{ev_id}_"):
            rep.problems.append(f"{ev_id}: file name should start with '{ev_id}_'")
        if sha256(path) != ev["sha256"]:
            rep.problems.append(f"{ev_id}: SHA-256 does not match the index (file changed after receipt)")
        limit = FRESHNESS_DAYS.get(ev["evidence_type"], "bad")
        if limit == "bad":
            rep.problems.append(f"{ev_id}: unknown evidence_type '{ev['evidence_type']}'")
        elif limit is not None:
            generated = date.fromisoformat(ev["generated_date"])
            if generated < FIELDWORK_START - timedelta(days=limit):
                rep.problems.append(f"{ev_id}: {ev['evidence_type']} generated {generated}, older than {limit} days before fieldwork")
            if generated > FIELDWORK_END:
                rep.problems.append(f"{ev_id}: generated {generated}, after fieldwork ended")
        if ev["provided_by"] != AUDITOR and ev_id not in pbc_by_ev:
            rep.problems.append(f"{ev_id}: provided by {ev['provided_by']} but no evidence request tracks it")

    # 2. Evidence request list: valid statuses, timeliness as of the report date.
    for r in pbc:
        if r["status"] not in PBC_STATUSES:
            rep.problems.append(f"{r['request_id']}: bad status '{r['status']}'")
            continue
        state = pbc_state(r, as_of)
        due = date.fromisoformat(r["due_date"])
        row = dict(r, state=state, days_late="")
        if state == "Open":
            if as_of > due:
                row["days_late"] = str((as_of - due).days)
                rep.warnings.append(f"{r['request_id']}: overdue by {days((as_of - due).days)} ({r['owner']})")
        else:
            received = date.fromisoformat(r["received_date"])
            if received > due:
                row["days_late"] = str((received - due).days)
                rep.warnings.append(f"{r['request_id']}: received {days((received - due).days)} late")
            if r["evidence_id"] and r["evidence_id"] not in index:
                rep.problems.append(f"{r['request_id']}: marked {r['status']} but {r['evidence_id']} is not in the evidence index")
        rep.pbc_rows.append(row)

    # 3. Assessment plan: evidence exists, conclusions are supported, workpapers exist and agree.
    not_available = {}
    for r in pbc:
        if pbc_state(r, as_of) == "Not Available":
            for c in split_ids(r["controls"]):
                not_available.setdefault(c, []).append(r["request_id"])
    for p in plan:
        cid = p["control_id"]
        if p["result"] not in RESULTS:
            rep.problems.append(f"{cid}: result '{p['result']}' must be Satisfied or Other than satisfied")
        if p["result"] == "Other than satisfied" and not re.fullmatch(r"AHR-\d{4}-\d{3}", p["finding_id"]):
            rep.problems.append(f"{cid}: Other than satisfied needs a finding ID")
        if p["result"] == "Satisfied" and p["finding_id"]:
            rep.problems.append(f"{cid}: Satisfied control should not carry finding {p['finding_id']}")
        if p["result"] == "Satisfied" and cid in not_available:
            rep.problems.append(f"{cid}: concluded Satisfied but required evidence was not available ({', '.join(not_available[cid])})")
        for ev_id in split_ids(p["evidence_ids"]):
            ev = index.get(ev_id)
            if ev is None:
                rep.problems.append(f"{cid}: needs {ev_id}, which is not in the evidence index")
                continue
            req = pbc_by_ev.get(ev_id)
            if ev["provided_by"] != AUDITOR and (req is None or pbc_state(req, as_of) == "Open"):
                rep.warnings.append(f"{cid}: waiting on {ev_id}")
        wp = root / "workpapers" / f"{p['workpaper']}.md"
        if not wp.exists():
            rep.problems.append(f"{cid}: workpaper {p['workpaper']}.md is missing")
            continue
        text = wp.read_text(encoding="utf-8")
        m = re.search(r"\*\*Conclusion:\*\*\s*(Satisfied|Other than satisfied)", text)
        if not m:
            rep.problems.append(f"{cid}: workpaper has no '**Conclusion:**' line")
        elif m.group(1) != p["result"]:
            rep.problems.append(f"{cid}: workpaper concludes '{m.group(1)}' but the plan says '{p['result']}'")
        for ev_id in split_ids(p["evidence_ids"]):
            if ev_id not in text:
                rep.problems.append(f"{cid}: workpaper does not cite {ev_id}")
    return rep


def write_hashes(root: Path = ROOT) -> int:
    path = root / "pbc" / "evidence_index.csv"
    rows = read_csv(path)
    changed = 0
    for r in rows:
        f = root / "evidence" / r["file"]
        if f.exists() and not r["sha256"]:
            r["sha256"] = sha256(f)
            changed += 1
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return changed


def render(rep: Report) -> str:
    counts = {}
    for r in rep.pbc_rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    lines = [
        f"Evidence status as of {rep.as_of}",
        "",
        "Requests: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())),
        "",
        f"{'Request':<8} {'Evidence':<9} {'Status':<14} {'Late':>4}  Owner",
    ]
    for r in rep.pbc_rows:
        lines.append(f"{r['request_id']:<8} {r['evidence_id']:<9} {r['state']:<14} {r['days_late']:>4}  {r['owner']}")
    lines.append("")
    lines.append("Problems:" if rep.problems else "Problems: none")
    lines += [f"  - {p}" for p in rep.problems]
    lines.append("Follow-ups:" if rep.warnings else "Follow-ups: none")
    lines += [f"  - {w}" for w in rep.warnings]
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Check the evidence trail behind an assessment")
    p.add_argument("--as-of", type=date.fromisoformat, default=FIELDWORK_END)
    p.add_argument("--write-hashes", action="store_true", help="fill blank sha256 cells in the index")
    args = p.parse_args(argv)
    if args.write_hashes:
        print(f"recorded {write_hashes()} new hashes")
        return 0
    rep = check(as_of=args.as_of)
    print(render(rep))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
