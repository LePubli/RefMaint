FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./

<<<<<<< HEAD
# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely.
RUN npm ci
=======
RUN npm ci --include=dev
>>>>>>> 61c8179e45f9f45bcee820e79ba28099bb4380af

COPY . .

RUN npx vite build

# Fail the build loudly if dist/ wasn't produced, instead of nginx
# silently serving an empty/stale directory
RUN test -f dist/index.html || (echo "ERREUR: le build Vite n'a pas produit dist/index.html" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
