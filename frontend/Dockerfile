# Estágio 1: Desenvolvimento (usado pelo docker-compose.dev.yml)
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
# --no-audit e --no-fund economizam processamento e metadados
RUN npm install --quiet --no-audit --no-fund
COPY . .
EXPOSE 5173

# Estágio 2: Build de Produção
FROM development AS build
# Remove dependências de dev antes de buildar (opcional para diminuir o estágio intermediário)
RUN npm run build

# Estágio 3: Produção (AQUI É ONDE ELA FICA COM ~20MB)
FROM nginx:alpine AS production
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]