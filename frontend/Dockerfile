FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Forcer NODE_ENV=development dans la commande elle-même pour garantir
# l'installation des devDependencies (vite, tsc…) quelle que soit la
# valeur injectée par la plateforme (Coolify, etc.)
RUN NODE_ENV=development npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
