-- Fails if any issue/PR was closed before it was created (impossible in real data).
select issue_key, created_at, closed_at
from {{ ref('stg_github__issues') }}
where closed_at < created_at