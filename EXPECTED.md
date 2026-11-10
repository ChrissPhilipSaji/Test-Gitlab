# dynamic-monorepo

## GitLab features
- Dynamic child pipeline: `generate-children` writes YAML, `run-children` runs it with `trigger:include:artifact`
- Nested generation: the child generates and triggers a grandchild pipeline
- Conditional generation: `GENERATE_DEPLOY=false` drops the package job
- Generated `parallel:matrix` job
- Monorepo: per-component `rules:changes`, `needs:` chains, `needs:optional`, shared job only when `libs/shared` changes
- `workflow:rules` to avoid duplicate branch + MR pipelines
- Two sample MRs: one touches only svc-a, one touches the shared lib (compare which jobs run)

## Expected GitHub mapping
- No child pipelines. Replace with a generator job that outputs a JSON matrix (`$GITHUB_OUTPUT`) and a `strategy.matrix` job using `fromJSON`. Nested generation and conditional stages usually need a rewrite.
- `rules:changes` -> a change-detection job (e.g. `dorny/paths-filter`) whose outputs gate downstream jobs with `if:`.
- Workflow-level `paths:` filters are all-or-nothing, so use the detection job.
- `needs:optional` -> `needs:` plus `if: always() && !failure()` patterns.
- Required status checks: a skipped workflow never reports, so keep one always-running summary job as the required check.
