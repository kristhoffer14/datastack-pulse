-- One row per issue or pull request, enriched with the repo key and cycle time.
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
    i.created_at,
    i.closed_at,
    i.merged_at,
    (i.state = 'closed') as is_closed,
    case
        when i.closed_at is not null
        then extract(epoch from (i.closed_at - i.created_at)) / 3600.0
    end as hours_to_close
from {{ ref('stg_github__issues') }} as i
left join {{ ref('dim_repo') }} as r
    on i.repo_full_name = r.repo_full_name