FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .

# Afficher les fichiers de configuration pour debug
RUN ls -la && echo "=== vite.config ===" && cat vite.config.* 2>/dev/null || echo "No vite config found"

# Build avec Vite et afficher les erreurs complètes
RUN npx vite build --debug 2>&1 || (echo "=== BUILD FAILED ===" && exit 1)

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
