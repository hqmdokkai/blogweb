# Stage 1: Build stage
FROM python:3.11-slim AS build

WORKDIR /app

# Sao chép tệp yêu cầu
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng
COPY . .

# Stage 2: Runtime stage
FROM httpd:alpine

# Cài đặt Apache mod_proxy
RUN apk add --no-cache apache2-utils \
    && sed -i '/^#LoadModule proxy_module/s/^#//' /usr/local/apache2/conf/httpd.conf \
    && sed -i '/^#LoadModule proxy_http_module/s/^#//' /usr/local/apache2/conf/httpd.conf

# Sao chép mã nguồn từ build stage vào image
COPY --from=build /app /usr/local/apache2/htdocs/app

# Cấu hình Apache để reverse proxy đến Flask app
RUN echo 'ProxyPass / http://localhost:8000/' >> /usr/local/apache2/conf/httpd.conf \
    && echo 'ProxyPassReverse / http://localhost:8000/' >> /usr/local/apache2/conf/httpd.conf

# Expose port 80
EXPOSE 80

# Khởi chạy Apache
CMD ["httpd", "-D", "FOREGROUND"]

