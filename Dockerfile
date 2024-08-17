# Stage 1: Build Python Application
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Setup Nginx with the Python Application
FROM nginx:alpine

# Install bash for scripting
RUN apk add --no-cache bash

# Remove the default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Add the Nginx configuration directly in Dockerfile
RUN echo 'server {\n\
    listen 80;\n\
    server_name _;\n\
    location / {\n\
        proxy_pass http://localhost:8000;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Copy the application from the build stage
COPY --from=build /app /app

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

