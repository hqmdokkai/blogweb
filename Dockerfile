# Stage 1: Build Python Application
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Setup Apache with the Python Application
FROM httpd:alpine

# Install bash and Apache modules
RUN apk add --no-cache bash apache2-utils

# Copy the Apache configuration file
COPY apache-config.conf /usr/local/apache2/conf/httpd.conf

# Copy the application from the build stage
COPY --from=build /app /app

# Expose port 80
EXPOSE 80

# Start Apache
CMD ["httpd", "-D", "FOREGROUND"]

