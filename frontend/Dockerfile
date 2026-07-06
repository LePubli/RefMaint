FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .
# Juste avant RUN npx vite build, ajoutez :
RUN ls -la && cat package.json
# Build directement avec Vite (évite les problèmes de scripts npm)
RUN npx vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
