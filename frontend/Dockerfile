FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=dev

COPY . .

ENV PATH="/app/node_modules/.bin:$PATH"

# Séparer les commandes pour voir laquelle échoue
# Étape 1 : Compilation TypeScript
RUN npx tsc -b

# Étape 2 : Build Vite
RUN npx vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
