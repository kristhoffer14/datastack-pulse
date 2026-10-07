# datastack-pulse
End-to-end ELT pipeline on the GitHub API: Python, dbt, Airflow, Postgres.

~20k items, 69 MB, con carga diaria de ~150 items

## Findings (v1)

**Method.** Cohort of issues and PRs created between 2026-07-10 and 30 days
before the run date, so every item has at least 30 days of follow-up. Items
still open count as "not closed". Percentages are only reported when n >= 100.

| Repo | PRs (n) | PR closed ≤7d | PR closed ≤30d | Issues (n) | Issue closed ≤7d | Issue closed ≤30d |
|---|---|---|---|---|---|---|
| PrefectHQ/prefect | 463 | 72.4% | 90.9% | 105 | 59.0% | 75.2% |
| duckdb/duckdb | 1,139 | 71.6% | 82.9% | 502 | 37.3% | 61.0% |
| dbt-labs/dbt-core | 361 | 69.0% | 77.0% | 360 | 17.5% | 45.6% |
| apache/spark | 1,371 | 66.6% | 82.0% | 24 | n/a | n/a |
| delta-io/delta | 411 | 65.5% | 76.9% | 31 | n/a | n/a |
| apache/airflow | 2,635 | 58.7% | 78.2% | 322 | 24.8% | 42.9% |
| apache/iceberg | 695 | 46.2% | 58.4% | 159 | 8.8% | 17.6% |
| dagster-io/dagster | 146 | 25.3% | 30.1% | 38 | n/a | n/a |

**Takeaways**
- PRs are resolved far faster than issues in nearly every project.
- Prefect is the only project where issues close almost as fast as PRs.
- Iceberg shows the slowest turnaround on both issues and PRs.

**Limitations**
- Window covers recently updated items only, not each repo's full history.
- "Closed" includes merged and rejected PRs; bot-authored items not yet filtered.
- Small samples (n < 100) are suppressed.