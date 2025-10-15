#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting deployment at $(date)"

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Login to Docker Hub
echo "Logging into Docker Hub..."
echo "${docker_token}" | docker login -u "${docker_username}" --password-stdin

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory
mkdir -p /home/ubuntu/app
cd /home/ubuntu/app

# Create docker-compose.yml
echo "Creating docker-compose.yml..."
cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: repairshop
      POSTGRES_PASSWORD: ${db_password}
      POSTGRES_DB: repair_shop_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U repairshop -d repair_shop_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: ${docker_username}/repair-shop-api:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://repairshop:${db_password}@db:5432/repair_shop_db
      ENVIRONMENT: production
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
DOCKEREOF

# Set ownership
chown -R ubuntu:ubuntu /home/ubuntu/app

# Start services
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check status
docker-compose ps

# Mark completion
echo "Deployment complete at $(date)" > /home/ubuntu/deployment-complete.txt

echo "Setup finished successfully!"
