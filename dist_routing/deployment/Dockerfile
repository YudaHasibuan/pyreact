# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python, Gunicorn & Nginx
FROM python:3.11-slim
WORKDIR /app

# Install Nginx and other utilities
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy Nginx config
COPY deployment/nginx.conf /etc/nginx/sites-available/default

# Copy Python requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend application files
COPY backend/ ./

# Copy built frontend assets to Nginx html directory
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Expose port 80 (served by Nginx)
EXPOSE 80

# Startup script to run Gunicorn and Nginx
COPY deployment/start.sh ./
RUN chmod +x start.sh

CMD ["./start.sh"]
