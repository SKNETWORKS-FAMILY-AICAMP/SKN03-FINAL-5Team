FROM node:18

WORKDIR /app

# ESLint 설정 파일을 먼저 복사
COPY .eslintrc.json ./

# package.json 및 종속성 파일 복사 및 설치
COPY package*.json ./
RUN npm install

# 환경 변수 설정
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV ESLINT_NO_DEV_ERRORS=true

# 나머지 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]