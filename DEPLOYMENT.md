# 🚀 JurisFind Hybrid Deployment Guide

This guide shows you how to deploy JurisFind with a **hybrid architecture**:
- **Backend**: Azure VM + Docker + Nginx
- **Frontend**: Vercel

## 📋 Prerequisites

- Azure VM (Ubuntu 20.04+)
- Vercel account
- Azure Storage Account
- Groq API key

## 🔧 Part 1: Backend Deployment (Azure VM)

### Step 1: Prepare Your Azure VM

```bash
# SSH into your Azure VM
ssh your-username@your-vm-ip

# Clone your repository
git clone https://github.com/Sagar-S-R/JurisFind.git
cd JurisFind
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your actual credentials
nano .env
```

Add your credentials:
```env
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
GROQ_API_KEY="your_groq_api_key_here"
GROQ_MODEL="llama3-70b-8192"
```

### Step 3: Update Nginx Configuration

```bash
# Edit nginx.conf to allow your Vercel domain
nano nginx.conf
```

Replace `https://your-jurisfind-app.vercel.app` with your actual Vercel URL.

### Step 4: Deploy Backend

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This will:
- ✅ Install Docker and Docker Compose
- ✅ Build and start containers
- ✅ Set up auto-start on boot
- ✅ Configure log rotation

### Step 5: Configure Azure VM Firewall

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Step 6: Upload Data and Generate Index

```bash
# Make management script executable
chmod +x manage.sh

# Upload PDFs to Azure (if you have local PDFs)
./manage.sh upload

# Generate FAISS index from Azure PDFs
./manage.sh index

# Test the integration
./manage.sh test
```

## 🌐 Part 2: Frontend Deployment (Vercel)

### Step 1: Update Frontend Configuration

Edit `frontend/vercel.json` and replace with your VM's public IP or domain:

```json
{
  "env": {
    "VITE_API_BASE_URL": "http://YOUR_VM_IP"
  }
}
```

### Step 2: Update API Base URL in Frontend

Edit `frontend/src/App.jsx` or wherever you define the API base URL:

```javascript
// Update this with your VM's public IP
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://YOUR_VM_IP';
```

### Step 3: Deploy to Vercel

```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy to Vercel
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set build command: npm run build
# - Set output directory: dist
```

### Step 4: Configure Environment Variables in Vercel

In Vercel dashboard:
1. Go to your project settings
2. Add environment variable:
   - Name: `VITE_API_BASE_URL`
   - Value: `http://YOUR_VM_IP` or `https://your-domain.com`

### Step 5: Update Backend CORS

Update `nginx.conf` on your VM with your Vercel URL:

```bash
# SSH into VM
ssh your-username@your-vm-ip
cd JurisFind

# Edit nginx configuration
nano nginx.conf
```

Replace:
```nginx
add_header Access-Control-Allow-Origin "https://your-actual-vercel-url.vercel.app" always;
```

Restart containers:
```bash
./manage.sh restart
```

## 🎯 Management Commands

Use the `manage.sh` script for easy management:

```bash
# Start/stop containers
./manage.sh start
./manage.sh stop
./manage.sh restart

# Check status and logs
./manage.sh status
./manage.sh logs

# Data management
./manage.sh upload    # Upload PDFs to Azure
./manage.sh index     # Generate FAISS index
./manage.sh test      # Run integration tests

# Maintenance
./manage.sh backup    # Create backup
./manage.sh update    # Update and rebuild
./manage.sh cleanup   # Clean Docker resources

# Debugging
./manage.sh shell     # Open shell in container
./manage.sh health    # Check API health
```

## 🔍 Testing Your Deployment

### Backend API Test

```bash
# Test API health
curl http://YOUR_VM_IP/api/health

# Test search endpoint
curl -X POST http://YOUR_VM_IP/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "contract law", "top_k": 5}'
```

### Frontend Test

1. Visit your Vercel URL
2. Try searching for legal documents
3. Check browser console for any CORS errors

## 🛡️ Security Considerations

### SSL/HTTPS Setup (Recommended)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Update nginx.conf to use HTTPS
# Uncomment the HTTPS server block in nginx.conf
```

### Firewall Configuration

```bash
# More restrictive firewall (optional)
sudo ufw deny 22      # Disable SSH from everywhere
sudo ufw allow from YOUR_IP to any port 22  # Allow SSH only from your IP
```

## 📊 Monitoring

### Check Container Status

```bash
./manage.sh status
```

### View Logs

```bash
# All containers
./manage.sh logs

# Specific container
./manage.sh logs jurisfind_backend
./manage.sh logs jurisfind_nginx
```

### Resource Monitoring

```bash
# Real-time container stats
docker stats

# System resources
htop
df -h
```

## 🚨 Troubleshooting

### Common Issues

**1. CORS Errors**
- Check nginx.conf has correct Vercel URL
- Restart containers: `./manage.sh restart`

**2. API Not Responding**
- Check container status: `./manage.sh status`
- Check logs: `./manage.sh logs jurisfind_backend`

**3. Azure Connection Issues**
- Test connection: `./manage.sh test`
- Check .env file has correct connection string

**4. Container Won't Start**
- Check Docker logs: `docker-compose logs`
- Check available disk space: `df -h`
- Check memory: `free -h`

### Quick Fixes

```bash
# Restart everything
./manage.sh restart

# Rebuild containers
docker-compose down
docker-compose up --build -d

# Check Docker system
docker system df
docker system prune -f  # Clean up space
```

## 🎉 Success!

Your JurisFind application is now running with:

- **Backend**: `http://YOUR_VM_IP` (API endpoints)
- **Frontend**: `https://your-app.vercel.app` (Web interface)
- **Auto-start**: Containers restart automatically on VM reboot
- **Monitoring**: Health checks and logging enabled
- **Security**: Nginx reverse proxy with CORS configuration

## 📈 Next Steps

1. **Set up monitoring** (Grafana + Prometheus)
2. **Configure SSL certificates** for HTTPS
3. **Set up automated backups**
4. **Configure log aggregation**
5. **Add CDN** for static assets

You now have a production-ready legal document search platform! 🚀