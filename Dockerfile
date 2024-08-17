# Sử dụng image Ubuntu làm base
FROM ubuntu:20.04

# Cài đặt Apache và các gói cần thiết
RUN apt-get update && \
    apt-get install -y apache2 python3 python3-pip python3-venv apache2-utils libapache2-mod-wsgi-py3

# Tạo thư mục cho ứng dụng
WORKDIR /app

# Copy ứng dụng vào container
COPY . /app

# Cài đặt các phụ thuộc Python
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Cấu hình Apache để sử dụng mod_wsgi
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Mở cổng 80
EXPOSE 80

# Khởi động Apache
CMD ["apachectl", "-D", "FOREGROUND"]


