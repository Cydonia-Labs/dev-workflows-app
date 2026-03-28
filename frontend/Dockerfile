FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# envsubst only replaces BACKEND_URL and PORT, leaving nginx variables intact
ENV BACKEND_URL=http://localhost:8000
ENV PORT=80
CMD ["sh", "-c", "envsubst '${BACKEND_URL} ${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
