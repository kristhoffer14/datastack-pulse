"""Daily ELT pipeline for datastack-pulse.

Loads GitHub repo snapshots and issues into Supabase (raw schema) in parallel,
checks source freshness, then runs `dbt build` (models, tests and snapshots).
"""

from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

DBT_DIR = "/usr/local/airflow/include/dbt"
DBT_BIN = "/usr/local/airflow/dbt_venv/bin/dbt"


@dag(
    dag_id="datastack_pulse_daily",
    schedule="0 6 * * *",  # 06:00 UTC, safely after the UTC day boundary
    start_date=datetime(2026, 10, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["datastack-pulse", "elt"],
    doc_md=__doc__,
)
def datastack_pulse_daily():
    @task
    def load_repo_snapshots():
        # Import inside the task: the DAG file is parsed often and the extractor
        # modules are only mounted where tasks run.
        import extract_repos

        extract_repos.main()

    @task
    def load_issues():
        import extract_issues

        extract_issues.main(since_days=90)  # only used on a repo's first run

    dbt_source_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"cd {DBT_DIR} && {DBT_BIN} source freshness",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_DIR} && {DBT_BIN} build",
    )

    [load_repo_snapshots(), load_issues()] >> dbt_source_freshness >> dbt_build


datastack_pulse_daily()