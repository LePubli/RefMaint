FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./

# npm ci with a clean, deterministic install avoids the known npm optional-
# dependencies bug that breaks Rollup/esbuild native binaries on Alpine/musl
# (build fails silently before producing dist/). Debian slim uses glibc,
# which sidesteps the issue entirely.
RUN npm ci --include=dev

COPY . .

# Rendre node_modules/.bin explicitement disponible dans le PATH
# pour garantir que tsc et vite sont trouvés quel que soit l'environnement
ENV PATH="/app/node_modules/.bin:$PATH"

# Type-check puis build. Pas de pipe vers tee ici : "cmd | tee file" renvoie
# le code de sortie de tee (quasi toujours 0), ce qui masquait les erreurs
# réelles de build et ne les faisait remonter à Docker/Coolify.
RUN npx tsc -b
RUN npx vite build

# Filet de sécurité : si vite build a réussi mais n'a pas produit dist/,
# on échoue explicitement plutôt que de laisser nginx servir un dossier vide.
RUN test -f dist/index.html || (echo "ERREUR: le build Vite n'a pas produit dist/index.html" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
