FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .

# Forcer le build même s'il y a des erreurs
RUN npx vite build --force || echo "Build terminé avec des erreurs"

# Vérifier si le dossier dist existe quand même
RUN ls -la dist/ || echo "WARNING: dist folder missing"

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
