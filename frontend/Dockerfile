FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Forcer l'installation des devDependencies (vite, typescript, etc.)
# même si NODE_ENV=production est injecté par la plateforme de déploiement
RUN npm ci --include=dev

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
