# Estágio 1: Desenvolvimento (Node.js)
FROM node:18-alpine as development

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Estágio 2: Build (Gera os arquivos estáticos)
FROM development as build
RUN npm run build

# Estágio 3: Produção (Nginx)
FROM nginx:stable-alpine as production

COPY --from=build /app/dist /usr/share/nginx/html

# Copia configuração customizada do Nginx (opcional, para lidar com SPA routes)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]