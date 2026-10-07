-- One row per repo per day. Flattens the raw jsonb payload into typed columns.
with source as (

    select * from {{ source('github', 'repo_snapshots') }}

)

select
    repo_full_name || ':' || snapshot_date::text   as snapshot_key,
    repo_full_name,
    snapshot_date,
    (payload ->> 'id')::bigint                     as repo_id,
    payload ->> 'name'                             as repo_name,
    payload -> 'owner' ->> 'login'                 as owner_login,
    payload ->> 'description'                      as description,
    payload ->> 'language'                         as primary_language,
    payload -> 'license' ->> 'spdx_id'             as license_spdx_id,
    (payload ->> 'stargazers_count')::int          as stars_count,
    (payload ->> 'forks_count')::int               as forks_count,
    (payload ->> 'subscribers_count')::int         as watchers_count,
    -- Note: GitHub's open_issues_count includes open pull requests
    (payload ->> 'open_issues_count')::int         as open_issues_and_prs_count,
    (payload ->> 'archived')::boolean              as is_archived,
    (payload ->> 'created_at')::timestamptz        as repo_created_at,
    (payload ->> 'pushed_at')::timestamptz         as last_pushed_at,
    _ingested_at
from source