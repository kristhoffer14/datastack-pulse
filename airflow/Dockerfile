FROM astrocrpublic.azurecr.io/runtime:3.3-9

# --- datastack-pulse customizations ---

# dbt lives in its own virtualenv to avoid dependency conflicts with Airflow
RUN python -m venv /usr/local/airflow/dbt_venv && /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres

# Make the extractor modules importable as top-level modules (e.g. `import extract_issues`)
ENV PYTHONPATH="${PYTHONPATH}:/usr/local/airflow/include/extract"

# dbt configuration inside the container
ENV DBT_PROFILES_DIR=/usr/local/airflow/include/dbt
ENV DBT_TARGET_PATH=/tmp/dbt_target
ENV DBT_LOG_PATH=/tmp/dbt_logs