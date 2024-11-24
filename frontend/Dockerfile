# FROM node:18

# WORKDIR /app

# # package.json 및 종속성 파일 복사 및 설치
# COPY package*.json ./
# RUN npm install

# # 환경 변수 설정
# ENV NEXT_TELEMETRY_DISABLED=1
# ENV NODE_ENV=production
# ENV ESLINT_NO_DEV_ERRORS=true

# # 나머지 소스 코드 복사
# COPY . .

# # 빌드
# RUN npm run build

# EXPOSE 3000

# CMD ["npm", "start"]
FROM node:18

WORKDIR /app
# 전체 프로젝트 파일 복사
COPY . .

# npm install 실행
RUN npm install

# 환경 변수 설정
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV ESLINT_NO_DEV_ERRORS=true

# 빌드
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]