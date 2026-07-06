FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

# Forcer l'installation de TOUTES les dépendances (y compris devDependencies)
# même si NODE_ENV=production est défini par Coolify
RUN npm ci --include=dev

COPY . .

# Rendre node_modules/.bin explicitement disponible dans le PATH
ENV PATH="/app/node_modules/.bin:$PATH"

# Utiliser npx pour garantir l'utilisation des binaires locaux
RUN npx tsc -b && npx vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
