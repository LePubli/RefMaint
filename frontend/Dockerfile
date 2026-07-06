FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .

ENV PATH="/app/node_modules/.bin:$PATH"

# Afficher les erreurs TypeScript avec détails
RUN npx tsc -b --verbose || (echo "=== ERREURS TYPESCRIPT ===" && npx tsc -b --listFiles 2>&1 | tail -50 && exit 1)

# Si tsc passe, on fait le build Vite
RUN npx vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
