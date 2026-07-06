FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .

# Afficher la configuration pour debug
RUN echo "=== Files ===" && ls -la && echo "=== Vite Config ===" && cat vite.config.* 2>/dev/null || echo "No vite config"

# Tenter le build et capturer TOUTE la sortie
RUN npx vite build 2>&1 | tee /tmp/build.log || (echo "=== BUILD FAILED ===" && cat /tmp/build.log && exit 1)

# Vérifier si dist a été créé
RUN ls -la dist/ || (echo "ERROR: dist folder not created" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
