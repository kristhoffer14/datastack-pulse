-- One row per repository per day, with growth versus the previous snapshot.
select
    snapshot_key,
    repo_id,
    repo_full_name,
    snapshot_date,
    stars_count,
    forks_count,
    open_issues_and_prs_count,
    stars_count - lag(stars_count) over w as stars_delta,
    forks_count - lag(forks_count) over w as forks_delta,
    -- Gaps happen if a daily run is missed, so deltas may span more than one day
    snapshot_date - lag(snapshot_date) over w as days_since_prev_snapshot
from {{ ref('stg_github__repo_snapshots') }}
window w as (partition by repo_id order by snapshot_date)