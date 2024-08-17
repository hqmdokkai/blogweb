# Dùng image Python làm base image
FROM python:3.11-slim AS build

# Cài đặt các thư viện cần thiết
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Sao chép mã nguồn vào container
COPY . .

# Cài đặt Apache và các module cần thiết
FROM httpd:alpine
RUN apk add --no-cache bash
COPY --from=build /app /app

# Sao chép file cấu hình Apache vào container
COPY apache-config.conf /usr/local/apache2/conf/httpd.conf

# Expose port 80
EXPOSE 80

# Khởi động Apache
CMD ["httpd-foreground"]


