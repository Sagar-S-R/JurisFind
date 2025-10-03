#!/bin/bash

# JurisFind Backend Deployment Script for Azure VM
# This script sets up Docker and deploys the JurisFind API backend

set -e  # Exit on any error

echo "🚀 JurisFind Backend Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    
    # Install Docker's official GPG key
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo apt install -y docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Start and enable Docker
print_status "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        print_status "Copying .env.example to .env"
        cp .env.example .env
        print_warning "Please edit .env file with your actual configuration before running the application"
    else
        print_error ".env.example file not found. Please create .env file manually"
        exit 1
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p api/data/pdfs api/data/faiss_store api/logs ssl

# Set proper permissions
sudo chown -R $USER:$USER api/data api/logs ssl

# Build and start containers
print_status "Building and starting JurisFind containers..."

# Stop any existing containers
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start
docker-compose up --build -d

# Wait for containers to start
print_status "Waiting for containers to start..."
sleep 10

# Check container status
if docker-compose ps | grep -q "Up"; then
    print_success "Containers are running successfully!"
    
    # Display container status
    echo ""
    print_status "Container Status:"
    docker-compose ps
    
    # Display access information
    echo ""
    print_success "🎉 JurisFind Backend Deployment Complete!"
    echo ""
    echo "Access your API at:"
    echo "  - Local: http://localhost"
    echo "  - Public: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VM_IP')"
    echo ""
    echo "API Documentation:"
    echo "  - Swagger: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VM_IP')/docs"
    echo "  - ReDoc: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VM_IP')/redoc"
    echo ""
    echo "Health Check:"
    echo "  - curl http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VM_IP')/api/health"
    
else
    print_error "Some containers failed to start!"
    echo ""
    print_status "Container logs:"
    docker-compose logs
    exit 1
fi

# Optional: Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/jurisfind > /dev/null <<EOF
$(pwd)/api/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Create systemd service for auto-start on boot
print_status "Creating systemd service for auto-start..."
sudo tee /etc/systemd/system/jurisfind.service > /dev/null <<EOF
[Unit]
Description=JurisFind API Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable jurisfind.service

print_success "Systemd service created. JurisFind will auto-start on boot."

echo ""
print_success "🎯 Next Steps:"
echo "1. Update .env file with your actual Azure and Groq credentials"
echo "2. Update nginx.conf with your Vercel frontend URL"
echo "3. Upload your PDFs: docker exec jurisfind_backend python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs"
echo "4. Generate index: docker exec jurisfind_backend python helpers/azure_data_manager.py generate-index"
echo "5. Test integration: docker exec jurisfind_backend python tests/test_azure_integration.py"

echo ""
print_warning "IMPORTANT: Remember to configure your Azure VM firewall to allow traffic on ports 80 and 443"