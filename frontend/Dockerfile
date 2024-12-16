# Node.js LTS 버전 사용
FROM node:18

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm install

# 환경 변수 설정
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# 나머지 소스 코드 복사ㅌ
COPY . .

ARG AWS_DEFAULT_REGION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# 빌드
RUN npm run build

# 포트 노출
EXPOSE 3000

# 애플리케이션 시작 (모든 IP 주소에서 요청 수신)
CMD ["npm", "start", "--", "-H", "0.0.0.0"]
