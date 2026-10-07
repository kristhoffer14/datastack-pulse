-- One row per repository, using its most recent daily snapshot.
with ranked as (

    select
        *,
        row_number() over (
            partition by repo_id order by snapshot_date desc
        ) as snapshot_rank
    from {{ ref('stg_github__repo_snapshots') }}

)

select
    repo_id,
    repo_full_name,
    repo_name,
    owner_login,
    description,
    primary_language,
    license_spdx_id,
    is_archived,
    repo_created_at
from ranked
where snapshot_rank = 1