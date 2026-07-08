FROM node:20-bookworm-slim AS builder

WORKDIR /app

# npm's update-notifier hangs its own exit handler when stdout isn't a TTY
# (exactly the case in a Docker build), causing a deterministic
# "npm error Exit handler never called!" crash right after it prints
# "New major version of npm available!". CI=true and update-notifier=false
# both disable that check so npm ci can actually finish and install
# devDependencies (like typescript) instead of silently aborting mid-install.
ENV CI=true
ENV NPM_CONFIG_UPDATE_NOTIFIER=false

# The build host has a broken IPv6 route: Node's DNS resolver tries an AAAA
# address for registry.npmjs.org first, gets no response, and silently hangs
# until the OS-level TCP connect times out (~72s, matching the consistent
# stall seen in Coolify builds) before it can fall back to IPv4. That long
# hang is what was tripping npm's "Exit handler never called!" bug. Forcing
# IPv4-first resolution avoids the hang entirely.
ENV NODE_OPTIONS=--dns-result-order=ipv4first

COPY package.json package-lock.json ./

# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely. --no-audit/--no-fund skip extra
# network round-trips to the registry that aren't needed for a build.
#
# DIAGNOSTIC: npm ci has been crashing deterministically ~72s in with
# "Exit handler never called!" across multiple unrelated fix attempts
# (update-notifier, IPv4-first DNS), which means the real cause is still
# unknown. npm always writes a detailed debug log to /root/.npm/_logs even
# when this bug swallows the console output, but that log is normally lost
# when the layer fails. Dumping it here on failure (still exiting non-zero
# so the build fails loudly) lets us see what npm was actually doing right
# before it died, instead of guessing again. Remove this once root-caused.
RUN npm ci --include=dev --no-audit --no-fund || (echo "===== npm debug log ====="; cat /root/.npm/_logs/*-debug-0.log 2>&1; echo "===== end npm debug log ====="; exit 1)

# Rendre node_modules/.bin explicitement disponible dans le PATH
# pour garantir que tsc et vite sont trouvés quel que soit l'environnement
ENV PATH="/app/node_modules/.bin:$PATH"

# Vérifier que TypeScript et Vite ont bien été installés localement avant de
# continuer, pour échouer avec un message clair plutôt que de laisser npx
# retomber sur un package npm sans rapport portant le même nom.
RUN test -x node_modules/.bin/tsc || (echo "ERREUR: TypeScript n'a pas été installé par npm ci" && exit 1)
RUN test -x node_modules/.bin/vite || (echo "ERREUR: Vite n'a pas été installé par npm ci" && exit 1)

COPY . .

# Utiliser directement les binaires locaux (pas npx) pour ne jamais risquer
# un fallback silencieux vers un package du registre npm portant le même nom.
RUN tsc -b
RUN vite build

# Filet de sécurité : si vite build a réussi mais n'a pas produit dist/,
# on échoue explicitement plutôt que de laisser nginx servir un dossier vide.
RUN test -f dist/index.html || (echo "ERREUR: le build Vite n'a pas produit dist/index.html" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
