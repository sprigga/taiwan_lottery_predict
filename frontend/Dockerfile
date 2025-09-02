# 多階段構建 Dockerfile
# 第一階段：構建應用
FROM node:18-alpine AS build-stage

WORKDIR /app

# 複製 package 文件
COPY package*.json ./

# 安裝依賴
RUN npm ci --only=production

# 複製源代碼
COPY . .

# 構建應用
# RUN npm run build

# 第二階段：生產環境
FROM nginx:alpine AS production-stage

# 複製自定義 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 從構建階段複製構建結果
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]