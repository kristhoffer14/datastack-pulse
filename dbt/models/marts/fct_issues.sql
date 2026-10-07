{{
    config(
        materialized='incremental',
        unique_key='issue_key',
        incremental_strategy='delete+insert'
    )
}}

-- One row per issue or pull request, enriched with the repo key and cycle time.
-- Incremental: only rows (re)loaded since the last run are processed.
select
    i.issue_key,
    r.repo_id,
    i.repo_full_name,
    i.issue_number,
    i.is_pull_request,
    i.state,
    i.state_reason,
    i.author_association,
    i.comments_count,
    i.labels_count,
    i.created_at,
    i.closed_at,
    i.merged_at,
    (i.state = 'closed') as is_closed,
    case
        when i.closed_at is not null
        then extract(epoch from (i.closed_at - i.created_at)) / 3600.0
    end as hours_to_close,
    i.author_type,
    (i.merged_at is not null) as is_merged,
    i._ingested_at
from {{ ref('stg_github__issues') }} as i
left join {{ ref('dim_repo') }} as r
    on i.repo_full_name = r.repo_full_name

{% if is_incremental() %}
where i._ingested_at > (select max(_ingested_at) from {{ this }})
{% endif %}