"""Pick a reproducible audit sample.

Sample sizes follow the (fictional) Acme Internal Audit methodology in
docs/sampling_guide.md. They are an organizational choice, not a NIST requirement:
SP 800-53A leaves depth and coverage to the assessor.

    python src/sampling.py evidence/E-02_hr_role_grants_2026-05-01_to_2026-09-30.csv \
        --id-column grant_id --seed 20260928
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

# Recurring controls: sample size by how often the control operates.
FREQUENCY_SAMPLE = {
    "annual": 1,
    "quarterly": 2,
    "monthly": 2,
    "weekly": 5,
    "daily": 20,
    "multiple-daily": 25,
}

# Event-driven controls (each grant, change, or ticket is one occurrence):
# (largest population in band, sample size). None means "test every item".
POPULATION_BANDS = [
    (10, None),
    (50, 10),
    (250, 25),
    (float("inf"), 40),
]


def sample_size_for_population(population: int) -> int:
    if population < 0:
        raise ValueError("population cannot be negative")
    for upper, size in POPULATION_BANDS:
        if population <= upper:
            return population if size is None else min(size, population)
    raise AssertionError("unreachable")


def sample_size_for_frequency(frequency: str, occurrences: int | None = None) -> int:
    key = frequency.lower()
    if key not in FREQUENCY_SAMPLE:
        raise ValueError(f"unknown frequency '{frequency}'; use one of {', '.join(FREQUENCY_SAMPLE)}")
    size = FREQUENCY_SAMPLE[key]
    return size if occurrences is None else min(size, occurrences)


def select_sample(items: list[str], size: int, seed: int) -> list[str]:
    """Random selection without replacement. The same seed always gives the same sample,
    so a reviewer can re-perform the selection from the workpaper."""
    if size > len(items):
        raise ValueError(f"sample size {size} is larger than the population {len(items)}")
    if len(set(items)) != len(items):
        raise ValueError("population items must be unique")
    chosen = random.Random(seed).sample(sorted(items), size)
    return sorted(chosen)


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_population(path: Path, id_column: str) -> list[str]:
    rows = read_csv(path)
    if rows and id_column not in rows[0]:
        raise ValueError(f"column '{id_column}' not found in {path.name}")
    return [r[id_column] for r in rows]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Select a reproducible audit sample")
    p.add_argument("population_csv", type=Path)
    p.add_argument("--id-column", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--size", type=int, help="override the methodology sample size")
    args = p.parse_args(argv)
    try:
        items = load_population(args.population_csv, args.id_column)
        size = args.size if args.size is not None else sample_size_for_population(len(items))
        chosen = select_sample(items, size, args.seed)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"Population: {len(items)}   Sample size: {size}   Seed: {args.seed}")
    for item in chosen:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
