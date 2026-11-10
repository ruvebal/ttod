FROM node:22-alpine AS build
WORKDIR /app
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=${BACKEND_URL}
# F23 (AA2): extra hostnames for Astro security.allowedDomains, baked in at build time.
ARG TTOD_ALLOWED_HOSTS=""
ENV TTOD_ALLOWED_HOSTS=${TTOD_ALLOWED_HOSTS}
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV HOST=0.0.0.0 PORT=4321 NODE_ENV=production
COPY --from=build /app/package.json /app/package-lock.json* ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
EXPOSE 4321
CMD ["node", "./dist/server/entry.mjs"]
