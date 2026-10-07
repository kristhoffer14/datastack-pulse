-- One row per issue or pull request (the GitHub issues API returns both).
with source as (

    select * from {{ source('github', 'issues') }}

)

select
    repo_full_name || ':' || issue_id::text        as issue_key,
    repo_full_name,
    issue_id,
    (payload ->> 'number')::int                    as issue_number,
    payload ->> 'title'                            as title,
    payload ->> 'state'                            as state,
    payload ->> 'state_reason'                     as state_reason,
    -- PRs carry a 'pull_request' key; plain issues do not
    (payload ? 'pull_request')                     as is_pull_request,
    payload -> 'user' ->> 'login'                  as author_login,
    payload ->> 'author_association'               as author_association,
    (payload ->> 'comments')::int                  as comments_count,
    (payload ->> 'created_at')::timestamptz        as created_at,
    updated_at,
    (payload ->> 'closed_at')::timestamptz         as closed_at,
    (payload -> 'pull_request' ->> 'merged_at')::timestamptz as merged_at,
    jsonb_array_length(payload -> 'labels') as labels_count,
    _ingested_at
from source