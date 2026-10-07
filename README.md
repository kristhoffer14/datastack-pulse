# datastack-pulse
End-to-end ELT pipeline on the GitHub API: Python, dbt, Airflow, Postgres.

~20k items, 69 MB, con carga diaria de ~150 items

## Findings (v1)

**Method.** Cohort of issues and PRs created between 2026-07-10 and 30 days
before the run date, so every item has at least 30 days of follow-up. Items
still open count as "not closed". Bot-authored items (GitHub accounts of type
`Bot`) are excluded. Percentages are only reported when n >= 100.

| Repo | PRs (n) | PR closed ≤7d | PR closed ≤30d | Issues (n) | Issue closed ≤7d | Issue closed ≤30d |
|---|---|---|---|---|---|---|
| duckdb/duckdb | 1,139 | 71.6% | 82.9% | 502 | 37.3% | 61.0% |
| apache/spark | 1,361 | 66.3% | 81.9% | 24 | n/a | n/a |
| delta-io/delta | 411 | 65.5% | 76.9% | 31 | n/a | n/a |
| dbt-labs/dbt-core | 313 | 64.2% | 73.5% | 354 | 17.8% | 45.5% |
| PrefectHQ/prefect | 170 | 54.7% | 78.8% | 103 | 59.2% | 75.7% |
| apache/airflow | 2,125 | 50.9% | 73.1% | 322 | 24.8% | 42.9% |
| apache/iceberg | 600 | 38.0% | 52.0% | 159 | 8.8% | 17.6% |
| dagster-io/dagster | 134 | 25.4% | 29.1% | 38 | n/a | n/a |

**Takeaways**
- Human-authored PRs are resolved faster than issues in most projects.
- Prefect is the exception: issues close as fast as PRs.
- Filtering bots matters: ~63% of Prefect's PRs were bot-authored, which
  inflated its PR close rate from 54.7% to 72.4% at 7 days.
- Among repos with enough issue data, Iceberg has the slowest issue turnaround.

**Limitations**
- Window covers recently updated items only, not each repo's full history.
- "Closed" includes both merged and rejected PRs.
- The bot filter only catches accounts registered as `Bot`; automation running
  under regular user accounts is not detected.
- Small samples (n < 100) are suppressed. Prefect issues (n = 103) are close
  to the threshold.