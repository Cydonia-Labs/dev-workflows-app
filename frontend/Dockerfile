FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# nginx:alpine auto-processes .template files in /etc/nginx/templates/
# using envsubst at container startup, resolving $PORT and $BACKEND_URL
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
