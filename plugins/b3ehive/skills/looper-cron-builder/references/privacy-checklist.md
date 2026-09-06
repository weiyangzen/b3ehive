# Looper Privacy Checklist

Use this checklist before committing or publishing Looper artifacts.

## Must Not Appear

- local absolute paths such as `<absolute-home-path>/<repo>/...`
- private repository names
- customer names or account identifiers
- personal strategy document paths
- internal product codenames
- raw user conversations
- API keys, access tokens, billing identifiers, or secrets
- private evidence directories
- exact local machine names or usernames

## Preferred Generic Names

- `repo_maintenance`
- `product_beta`
- `benchmark_lane`
- `claim_audit`
- `workflow_automation`
- `support_ops`
- `growth_experiment`
- `customer_workflow`
- `integration_repair`

## Local-Only Allowed Surface

Private names may exist only in ignored local surfaces when needed for actual
execution:

- `.cron/**`
- `.ops/**`
- `.b3ehive/looper/*.local.*`
- local environment variables
- local prompt files that are not committed
- local logs that are not committed

## Scan

Run a generic scan:

```bash
rg -n -i '(absolute home path|private repo|customer|secret|api[_-]?key|token|password)' .
```

Then run a project-specific denylist scan from a local-only file when the
operator provides one:

```bash
while IFS= read -r pattern; do
  [[ -z "$pattern" ]] && continue
  rg -n -i -- "$pattern" .
done < .b3ehive/looper/private_denylist.local.txt
```
