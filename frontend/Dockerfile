# 빌드 스테이지
FROM node:18 AS builder

WORKDIR /app

# 종속성 파일만 먼저 복사하여 캐시 활용
COPY package*.json ./
RUN npm ci

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# 실행 스테이지
FROM node:18-slim

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/next.config.mjs ./next.config.mjs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# 비특권 사용자로 전환
USER node

EXPOSE 3000

CMD ["npm", "start"]