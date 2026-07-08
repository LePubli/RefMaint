FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./

<<<<<<< HEAD
# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely.
RUN npm ci

>>>>>>> f6f90407881c3c04f6fce5f2455fa0befe2a008c

COPY . .

# Afficher la configuration pour debug
RUN echo "=== Files ===" && ls -la && echo "=== Vite Config ===" && cat vite.config.* 2>/dev/null || echo "No vite config"

# Tenter le build et capturer TOUTE la sortie
RUN npx vite build 2>&1 | tee /tmp/build.log || (echo "=== BUILD FAILED ===" && cat /tmp/build.log && exit 1)

# Vérifier si dist a été créé
RUN ls -la dist/ || (echo "ERROR: dist folder not created" && exit 1)

# Fail the build loudly if dist/ wasn't produced, instead of nginx
# silently serving an empty/stale directory
RUN test -f dist/index.html || (echo "ERREUR: le build Vite n'a pas produit dist/index.html" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
