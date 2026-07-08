FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./

# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely.
RUN npm ci

COPY . .

# Rendre node_modules/.bin explicitement disponible dans le PATH
# pour garantir que tsc et vite sont trouvés quel que soit l'environnement
ENV PATH="/app/node_modules/.bin:$PATH"

RUN tsc -b && vite build

# Fail the build loudly if dist/ wasn't produced, instead of nginx
# silently serving an empty/stale directory
RUN test -f dist/index.html || (echo "ERREUR: le build Vite n'a pas produit dist/index.html" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
