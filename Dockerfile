# Stage 1: Build the Python application
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Nginx setup
FROM nginx:alpine

# Copy the application files
COPY --from=build /app /app

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
