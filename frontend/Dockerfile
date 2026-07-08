FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./

# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely.
# Retry once: npm has a known intermittent bug ("Exit handler never called!")
# that can abort mid-install and leave devDependencies (like typescript)
# missing, which then makes "npx tsc" silently fall back to installing an
# unrelated npm package also named "tsc" instead of failing clearly.
RUN npm ci --include=dev || npm ci --include=dev

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
