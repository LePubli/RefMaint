---
name: Coolify concurrent multi-service build resource contention
description: Intermittent/non-deterministic Docker build failures on Coolify (npm crashes, exit 255, connection drops) across multiple services in one docker-compose.yml — check for host resource exhaustion, not just app-level bugs.
---

Coolify builds all services in a `docker-compose.yml` concurrently via
`docker buildx bake` (not sequentially), so a Node frontend image and a
Python backend image building at the same time compete for the host's
CPU/RAM/network. On a resource-constrained VPS this can produce **different
failure symptoms on different attempts** even though the root cause is the
same contention: one run might crash npm with a generic-looking bug
(`npm error Exit handler never called!`), another might sever the whole
build connection with a bare `exit code 255` and no application-level error
message at all.

**Why this matters:** chasing each symptom as its own app-level bug (npm
version quirks, DNS/IPv6 resolution, update-notifier) can burn many
iterations without progress if the actual cause is host memory/CPU pressure
during concurrent builds. A telltale sign: the failure point is suspiciously
consistent in elapsed time across attempts even after unrelated fixes, or
the failure mode itself changes between attempts (crash vs. connection
drop) while the surrounding build steps stay identical.

**How to apply:** before deep-diving into an npm/pip/language-specific bug
that only reproduces on the remote build host (never locally), audit each
Dockerfile in the compose project for unnecessary build-time load —
e.g. installing a compiler toolchain (`gcc`, `libpq-dev`) for Python
packages that actually ship prebuilt manylinux wheels (`psycopg2-binary`,
`bcrypt`, `cryptography`, `pillow` all do) is pure waste that adds CPU/
network/memory pressure for no benefit. Also ask the user to check the
Coolify host's available RAM/swap and `dmesg` for OOM-killer activity
during a failed build if trimming build load doesn't resolve it.
