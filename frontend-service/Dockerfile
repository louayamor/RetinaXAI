FROM node:20-alpine AS base

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1


FROM base AS deps

COPY package.json ./
RUN npm install --legacy-peer-deps


FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build


FROM base AS runtime

RUN addgroup --system nodegroup && \
    adduser --system --ingroup nodegroup nodeuser

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

USER nodeuser

EXPOSE 3000

ENV PORT=3000 \
    NEXT_PUBLIC_API_URL=http://backend-service:8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "server.js"]
