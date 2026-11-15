# Audit workflow

How Acme Internal Audit (fictional) moved from "assess these controls" to a defensible
conclusion for each one. The methods (examine, interview, test) and the idea of an assessment
objective come from NIST SP 800-53A Rev 5. The PBC list, sampling, and workpaper conventions
are common audit practice. The wording is mine.

```
Plan  →  Request  →  Collect  →  Test  →  Conclude  →  Report
 │         │           │          │          │            │
 plan     PBC list    evidence   control    workpaper    SAR finding
 .csv     .csv        index +    tests +    conclusion   (rmf-ato-package-templates)
                      SHA-256    sampling
```

## 1. Plan

For each control, write down in `procedures/assessment_plan.csv`:

- **Objective:** what must be true, in one plain sentence. SP 800-53A breaks each control into
  determination statements. I paraphrase the ones that matter for this system.
- **Methods:** *Examine* documents and records, *Interview* the people who run the control, and
  *Test* by re-performing it or checking the system directly. Testing gives the strongest evidence.
- **Assessment objects:** the specific records, people, or system parts to look at.
- **Coverage:** full population, a sample, or a single configuration.

Inherited controls are not retested. The assessor confirms the provider's authorization is
current and that the system is configured to use the control (see WP-IA-02-01).

## 2. Request (the PBC list)

"Provided by client" (PBC) is the audit term for evidence the system team has to produce. Each
row in `pbc/evidence_request_list.csv` names one item, an owner, and a due date. Write requests so
the owner cannot misread them: name the period, the fields needed, and the format.

Point-in-time exports (account lists, role lists, open vulnerabilities) are due on a fieldwork
day so the assessor can **watch the query run**. That rules out an edited spreadsheet.

## 3. Collect

When evidence arrives:

1. Name it `E-NN_short-description_date.ext` and save it unchanged in `evidence/`.
2. Add it to `pbc/evidence_index.csv` with its type (export, report, or document), source system,
   date generated, and who provided it.
3. Run `python src/evidence_check.py --write-hashes` to record its SHA-256 hash.

The hash shows the file hasn't changed since receipt. If anyone edits it later, even to "fix" a
typo, the checker flags it.

### What makes evidence good enough

| Quality | Question to ask | How this kit checks it |
|---|---|---|
| Relevant | Does it show this control operating for this system? | Plan links each control to specific evidence IDs |
| Reliable | Could someone have altered it before I got it? | Observed queries, assessor-run scans, SHA-256 |
| Sufficient | Is there enough to support the conclusion? | Population counts and sample sizes in each workpaper |
| Timely | Does it cover the period I'm concluding on? | Freshness limits by evidence type |

## 4. Test

Automated re-performance is in `src/control_tests.py`. Each test reads the evidence and reports
the population, the items tested, and the exceptions. Sampled tests use `src/sampling.py` with a
recorded seed, so a reviewer can re-select the same items (see `sampling_guide.md`).

Separate **exceptions** from **observations**:

- An *exception* means the control did not work as described, so the result is Other than satisfied.
- An *observation* is worth noting but stays within a stated tolerance. Example: one late SOC
  triage out of 32, against a 95% threshold.

## 5. Conclude

Each workpaper ends with exactly one line, `**Conclusion:** Satisfied` or
`**Conclusion:** Other than satisfied`. The checker reads that line and fails if:

- It disagrees with the plan
- An Other than satisfied control has no finding ID
- A Satisfied control relied on evidence marked Not Available
- The workpaper doesn't cite every evidence ID the plan lists

## 6. Report

Findings flow into the Security Assessment Report in
[rmf-ato-package-templates](https://github.com/CauseSpark/rmf-ato-package-templates/blob/main/examples/acme-hr-portal/sar.md).
Each one is risk-rated there and becomes a POA&M item, which is tracked in
[policy-and-poam-program](https://github.com/CauseSpark/policy-and-poam-program).

## Source

- [NIST SP 800-53A Rev 5, Assessing Security and Privacy Controls](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) (January 2022; Release 5.2.0, August 2025)
