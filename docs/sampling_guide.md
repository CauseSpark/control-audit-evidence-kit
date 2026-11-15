# Sampling guide

> These sample sizes are the **fictional Acme Internal Audit methodology**. They follow common
> audit practice, but NIST does not prescribe them. SP 800-53A leaves depth and coverage to the
> assessor. Use your own organization's methodology for real work.

## When to sample

Test the **full population** when it's small or can be checked by a query. Most automated checks
in this kit do that: all 19 accounts, all 7 open flaws, all 12 weeks of reviews. Sample only
when checking each item takes real effort, such as reading an approval ticket or a change record.

## Event-driven controls

These are controls that run each time something happens, like an access grant or a change.

| Population | Sample size |
|---|---|
| 1–10 | Test every item |
| 11–50 | 10 |
| 51–250 | 25 |
| 251 or more | 40 |

## Recurring controls

These are controls that run on a schedule.

| Frequency | Sample size |
|---|---|
| Annual | 1 |
| Quarterly | 2 |
| Monthly | 2 |
| Weekly | 5 |
| Daily | 20 |
| Several times a day | 25 |

## How to select

1. Get the full population and **check it's complete** against an independent source, such as
   the roster, CMDB, or release history.
2. Pick a seed. I use the date the selection was made (`20260928`).
3. Run `python src/sampling.py <population.csv> --id-column <column> --seed <seed>`.
4. Record the command in the workpaper.

The tool sorts the population before selecting, so the same seed gives the same sample however
the file is ordered. A reviewer can re-run the command and get the same items.

## When a sampled item fails

One exception in a sample means the control is not reliably working. Do not draw a second sample
to make the failure go away. Report it, and if the cause looks broader, consider testing the full
population to size the problem.
