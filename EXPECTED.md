# review-apps

Fake deploy: jobs only print and set the environment. GitLab still records real environments, so the migration behaviour is the same as with a real target.

## GitLab features
- Dynamic environment `review/$CI_COMMIT_REF_SLUG` with `url`, `on_stop`, `auto_stop_in: 2 days`
- Stop job (`action: stop`, `GIT_STRATEGY: none`), runs automatically when the MR is merged or the branch is deleted
- Two sample MRs (feature-login, feature-search) each get their own review environment
- A stale environment (`review/stale-old-branch`) created by the seed
- Scheduled pipeline (daily) that calls `environments/stop_stale`; set the `CLEANUP_TOKEN` variable to a token with `api` scope to make it act
- `workflow:rules` limited to MR events, default branch and schedules

## Expected GitHub mapping
- Trigger: `pull_request` with `types: [opened, synchronize, reopened, closed]`.
- Deploy job with `environment: { name: pr-${{ github.event.number }}, url: ... }`; GitHub creates the deployment record.
- Teardown: a job running `if: github.event.action == 'closed'` that deletes the environment (REST `DELETE /repos/{o}/{r}/environments/{name}` or deployments API set to inactive).
- `concurrency: group: review-${{ github.event.number }}` with `cancel-in-progress: true` to avoid races.
- `auto_stop_in` has no equivalent: add a scheduled workflow that lists environments and removes orphans.
