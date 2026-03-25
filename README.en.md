# DNSHE Auto Renew

[中文](./README.md) | [English](./README.en.md)

## Quick Start Summary

You only need two steps:

1. Create a new private GitHub repository and copy the contents of this repository into it
2. Add the required `Secrets` and `Variables` in your GitHub repository

Before doing that, you must first enable and create your `DNSHE API` credentials in the DNSHE dashboard.

DNSHE dashboard:

- https://my.dnshe.com

This repository provides a GitHub Actions based auto-renewal workflow for DNSHE free domains. The workflow runs weekly and only renews a domain after it enters its renewal window.

## Features

- Managed domains are not hard-coded in the repository
- The domain list is read from the repository variable `DNSHE_DOMAINS`
- `DNSHE_DOMAINS` uses one domain per line, so adding or removing domains only requires editing one repository variable
- When a domain is discovered for the first time, the script derives its initial expiration time from the DNSHE API field `created_at` using `created_at + 365 days`
- After a successful renewal, the script stores the returned `new_expires_at` in `state/domains-state.json`
- Future runs continue from the latest known expiration automatically

## Repository Settings

Add the following settings in your GitHub repository:

- Secret: `DNSHE_API_KEY`
- Secret: `DNSHE_API_SECRET`
- Variable: `DNSHE_DOMAINS`

`DNSHE_DOMAINS` should be plain text with one domain per line:

```text
abc88.cc.cd
12366.cc.cd
```

Usage:

- Add a domain: append one line to `DNSHE_DOMAINS`
- Remove a domain: delete one line from `DNSHE_DOMAINS`

## Renewal Rule

Each domain is processed with the following logic:

1. Read the domain from `DNSHE_DOMAINS`
2. Query DNSHE through `subdomains/list`
3. If the domain is new, derive the initial expiration time as `created_at + 365 days`
4. Compute the renewal trigger time as `renew_at = expires_at - renew_before_days`
5. Skip the domain if current time is earlier than `renew_at`
6. Renew the domain if current time is at or after `renew_at`
7. Update the state file with `new_expires_at` after a successful renewal

The default lead time before renewal is `175 days`.

## Example: Add a New Domain Later

Assume you currently manage these two domains:

```text
abc88.cc.cd
12366.cc.cd
```

Thirty days later, you register a new domain:

```text
444.cc.cd
```

You only need to update `DNSHE_DOMAINS` to:

```text
abc88.cc.cd
12366.cc.cd
444.cc.cd
```

On the next scheduled run, the workflow will:

1. Call DNSHE `subdomains/list`
2. Detect that `444.cc.cd` is not yet present in `state/domains-state.json`
3. Read its `created_at`
4. Compute the initial expiration as `created_at + 365 days`
5. Save that value into `state/domains-state.json`
6. Use `expires_at - 175 days` for future renewal-window checks

This means you do not need to manually enter either the registration time or the expiration time for newly added domains.

## Files

- `scripts/dnshe_auto_renew.py`: main renewal script
- `.github/workflows/dnshe-auto-renew.yml`: GitHub Actions workflow
- `state/domains-state.json`: generated or updated state file storing the latest known expiration time per domain

## Deployment Steps

1. Create a new private GitHub repository
2. Upload the contents of this folder to the repository root
3. In `Settings -> Secrets and variables -> Actions`, add:
   - Secret `DNSHE_API_KEY`
   - Secret `DNSHE_API_SECRET`
   - Variable `DNSHE_DOMAINS`
4. Open the `Actions` tab
5. Manually run `DNSHE Auto Renew` once to confirm the workflow can read the domains and create the state file

Notes:

- GitHub currently does not allow you to change the visibility of a fork
- If the upstream repository is public, the safest approach is to create your own private repository and copy the contents into it

## Workflow Behavior

- Runs once per week by default
- Uses GitHub Hosted Runners
- Scheduled runs use UTC
- The workflow file must stay on the default branch
- If you regenerate the DNSHE API credentials, update the GitHub Secrets as well

## First Run Behavior

If a domain has no existing state entry:

- The script reads `created_at` from the DNSHE API response
- It derives the initial expiration as `created_at + 365 days`
- It writes the result to `state/domains-state.json`

After a successful renewal:

- The script reads `new_expires_at` from the DNSHE API response
- The previous expiration is replaced automatically
- The next renewal window is recalculated from the new expiration time

## Local Dry Run

```powershell
$env:DNSHE_API_KEY='your_key'
$env:DNSHE_API_SECRET='your_secret'
$env:DNSHE_DOMAINS="abc88.cc.cd`n12366.cc.cd`n444.cc.cd"
python .\scripts\dnshe_auto_renew.py --state .\state\domains-state.json --dry-run
```

Notes:

- `--dry-run` only evaluates and logs the decision flow
- It does not call the renew endpoint
- It does not modify the state file

## Notes

- Initial expiration derivation depends on the DNSHE API returning `created_at`
- The current implementation assumes a `365-day` validity period
- If DNSHE changes the validity rule in the future, the derivation logic should be updated
