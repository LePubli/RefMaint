---
name: Replit package-firewall proxy leaking into committed lockfiles
description: npm/pip lockfiles generated inside Replit's dev environment can bake in an internal-only registry proxy hostname that breaks installs on any external host (Docker builds on Coolify, other CI, etc).
---

Replit's dev environment transparently points npm and pip at an internal
proxy (`http://package-firewall.replit.local/...`) via env vars
(`NPM_CONFIG_REGISTRY`, `PIP_INDEX_URL`). That hostname only resolves
inside Replit's network.

**Why this matters:** npm bakes the resolved download URL for every
package into `package-lock.json`'s `"resolved"` fields at the time the
lockfile is generated. If the lockfile was generated (or regenerated) while
running inside Replit, every one of those URLs points at
`package-firewall.replit.local` — permanently, until the lockfile is
regenerated again. Any external build environment (e.g. a Docker build on
Coolify, another CI system) that runs `npm ci` against that committed
lockfile will fail to fetch packages, since that hostname is unreachable
outside Replit. This produced *inconsistent, confusing symptoms* that
looked like unrelated bugs across several debugging attempts: npm's own
generic "Exit handler never called!" crash, a bare `ENOTFOUND`, and even a
build that got killed outright — all downstream of the same unreachable
host, differing only in how many failed requests it took before something
gave up. Critically, re-testing `npm ci` locally inside Replit to "verify"
a fix always looked fine, because Replit's own network resolves that
hostname — the bug only reproduces on the external host, which made local
verification actively misleading.

**How to apply:** if a Docker build (or any external CI) that runs `npm
ci`/`pip install` from a lockfile fails in ways that don't reproduce when
tested locally inside Replit, check whether the lockfile references
`package-firewall.replit.local` (`grep -c package-firewall.replit.local
package-lock.json`) or pip's config points at the same host
(`pip config list`). If so, regenerate the lockfile against the real
public registry (`npm install --registry=https://registry.npmjs.org/` from
a clean `node_modules`) and pin it going forward with a project-local
`.npmrc` (`registry=https://registry.npmjs.org/`) so future regenerations
inside Replit don't silently reintroduce the internal proxy URL.
