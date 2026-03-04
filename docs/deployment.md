# Deployment Guide

This document covers the full production deployment of JurisFind — the FastAPI backend on an Azure VM with Docker and Nginx, and the React frontend on Azure Static Web Apps, along with the CI/CD workflow and the process for pushing backend updates.

---

## Table of Contents

- [Infrastructure Overview](#infrastructure-overview)
- [Azure VM — Backend](#azure-vm--backend)
  - [VM Provisioning](#vm-provisioning)
  - [SSH Access](#ssh-access)
  - [Installing Docker and Nginx](#installing-docker-and-nginx)
  - [Cloning the Repository](#cloning-the-repository)
  - [Environment Configuration](#environment-configuration)
  - [Nginx Configuration](#nginx-configuration)
  - [Starting the API Container](#starting-the-api-container)
  - [Verifying the Backend](#verifying-the-backend)
- [Azure Static Web Apps — Frontend](#azure-static-web-apps--frontend)
  - [Creating the Static Web App](#creating-the-static-web-app)
  - [GitHub Actions Workflow](#github-actions-workflow)
  - [Setting GitHub Secrets](#setting-github-secrets)
  - [CORS Configuration](#cors-configuration)
- [Updating the Backend After a Code Change](#updating-the-backend-after-a-code-change)
- [Updating the Frontend](#updating-the-frontend)
- [Monitoring and Logs](#monitoring-and-logs)
- [Common Issues](#common-issues)

---

## Infrastructure Overview

| Component | Service | Details |
|---|---|---|
| Backend API | Azure VM (Standard D2alds v7) | Ubuntu 24.04, East US 2, `20.186.113.106` |
| Reverse Proxy | Nginx on VM | Port 80 → FastAPI port 8000 |
| Container Runtime | Docker + Docker Compose | API runs as a single container |
| Frontend | Azure Static Web Apps (free) | Global CDN, auto-deploy from GitHub |
| Storage | Azure Blob Storage | See [azure_integration.md](azure_integration.md) |
| CI/CD — frontend | GitHub Actions | Triggered on push to `main` |
| CI/CD — backend | Manual (`git pull` + `docker compose up`) | — |

---

## Azure VM — Backend

### VM Provisioning

If you are provisioning a new VM from scratch in the Azure Portal:

1. Go to **Virtual Machines** and click **+ Create**
2. Recommended settings:
   - Image: `Ubuntu Server 24.04 LTS`
   - Size: `Standard D2alds v7` (2 vCPUs, 4 GB RAM)
   - Region: East US 2
   - Authentication: SSH public key — generate a new key pair and download the `.pem` file
   - Inbound ports: allow SSH (22) and HTTP (80) in the NSG
3. After creation, note the public IP address

### SSH Access

On Windows, fix the `.pem` file permissions before SSH will accept it:

```powershell
$pem = "path\to\jurisfind-backend_key.pem"
icacls $pem /inheritance:r
icacls $pem /remove "NT AUTHORITY\Authenticated Users"
icacls $pem /remove "BUILTIN\Users"
icacls $pem /grant:r "$($env:USERDOMAIN)\$($env:USERNAME):(R)"
```

Then connect:

```powershell
ssh -i path\to\jurisfind-backend_key.pem azureuser@20.186.113.106
```

On Linux/macOS:

```bash
chmod 400 jurisfind-backend_key.pem
ssh -i jurisfind-backend_key.pem azureuser@20.186.113.106
```

### Installing Docker and Nginx

Run these on the VM after SSH-ing in:

```bash
sudo apt-get update -y
sudo apt-get install -y nginx

# Install Docker using the official script
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker azureuser

# Enable both services to start on boot
sudo systemctl enable docker nginx
sudo systemctl start docker nginx
```

Log out and back in for the Docker group change to take effect, or run `newgrp docker`.

Verify:

```bash
docker --version
nginx -v
```

### Cloning the Repository

```bash
sudo git clone https://github.com/Sagar-S-R/JurisFind.git /opt/jurisfind
sudo chown -R azureuser:azureuser /opt/jurisfind
```

### Environment Configuration

```bash
cp /opt/jurisfind/api/.env.example /opt/jurisfind/api/.env
nano /opt/jurisfind/api/.env
```

Set at minimum:

```env
GROQ_API_KEY=your_real_groq_api_key
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=jurisfindstore;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
AZURE_DATA_CONTAINER=data
USE_LOCAL_FILES=false
```

Save with `Ctrl+O`, then `Ctrl+X`.

The FAISS index and PDFs are loaded from Azure Blob Storage at container startup — no manual file copying is needed as long as you have completed the Blob upload step described in [azure_integration.md](azure_integration.md).

### Nginx Configuration

```bash
sudo cp /opt/jurisfind/nginx.conf /etc/nginx/sites-available/jurisfind
sudo ln -sf /etc/nginx/sites-available/jurisfind /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test config before applying
sudo nginx -t
sudo systemctl restart nginx
```

The `nginx.conf` in the project root proxies all traffic on port 80 to `127.0.0.1:8000`, applies rate limiting (30 requests/minute), enforces a 20 MB upload limit, and adds standard security headers.

### Starting the API Container

```bash
cd /opt/jurisfind
sudo docker compose up -d --build
```

The `docker-compose.yml` in the project root:
- Builds the image from `api/Dockerfile`
- Binds the container's port 8000 to `127.0.0.1:8000` (not exposed publicly — Nginx handles that)
- Mounts `./api/data` for the FAISS store volume
- Creates a named volume `confidential_tmp` for ephemeral confidential PDF uploads
- Reads environment variables from `./api/.env`

The first build takes several minutes because it installs all Python dependencies including `sentence-transformers` and `faiss-cpu`. Subsequent builds are faster due to Docker layer caching.

### Verifying the Backend

```bash
# Direct to FastAPI inside the container
curl http://localhost:8000/api/health

# Through Nginx (confirms the full proxy chain works)
curl http://20.186.113.106/api/health
```

Expected response:
```json
{"status": "healthy", "message": "Legal case search service is running", "total_cases": 46456}
```

---

## Azure Static Web Apps — Frontend

### Creating the Static Web App

1. In the Azure Portal, go to **Static Web Apps** and click **+ Create**
2. Fill in:
   - Resource group: same as the VM (`jurisFind`)
   - Name: `jurisfind`
   - Hosting plan: **Free**
   - Region: East US 2
   - Source: **GitHub**
   - Organization: `Sagar-S-R`
   - Repository: `JurisFind`
   - Branch: `main`
   - Build preset: **React** (or **Vite**)
   - App location: `./frontend`
   - Api location: leave empty
   - Output location: `dist`
3. Deployment authorization: **GitHub**
4. Click **Review + Create** then **Create**

Azure will automatically create and commit a GitHub Actions workflow file into your repository at `.github/workflows/azure-static-web-apps-xxx.yml`.

### GitHub Actions Workflow

The auto-generated workflow builds the frontend and deploys it. It needs the `VITE_API_BASE_URL` environment variable available at build time so that Vite bakes the correct API URL into the production bundle.

Edit the generated workflow file in your repo and add the env variable to the build step:

```yaml
- name: Build And Deploy
  uses: Azure/static-web-apps-deploy@v1
  with:
    azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
    repo_token: ${{ secrets.GITHUB_TOKEN }}
    action: "upload"
    app_location: "./frontend"
    output_location: "dist"
  env:
    VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
```

### Setting GitHub Secrets

In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret** and add:

| Secret Name | Value |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | The deployment token from the Static Web App in the Azure Portal (Static Web App → Manage deployment token) |
| `VITE_API_BASE_URL` | `http://20.186.113.106` |

After adding secrets, trigger a new deployment by pushing any commit to `main`.

### CORS Configuration

The frontend origin must be added to the CORS allowlist in `api/main.py`. The relevant section:

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://20.186.113.106",
    "https://blue-cliff-0dfeb910f.2.azurestaticapps.net",
],
```

After editing `main.py`, commit and push to `main`, then SSH into the VM and pull + rebuild (see below).

---

## Updating the Backend After a Code Change

The VM does not automatically pull changes from GitHub. The update process is manual:

```bash
# From your local machine
git add .
git commit -m "your change description"
git push origin main

# Then SSH into the VM
ssh -i jurisfind-backend_key.pem azureuser@20.186.113.106

# On the VM
cd /opt/jurisfind
git pull origin main
sudo docker compose up -d --build
```

The `--build` flag forces Docker to rebuild the image if any Python files or requirements changed. If only `nginx.conf` changed, reload Nginx instead:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

If only `api/.env` changed (e.g. rotating API keys), restart is enough without a rebuild:

```bash
sudo docker compose restart
```

### Automating Backend Deploys (Optional)

To make backend deploys automatic on push to `main`, you can add a GitHub Actions workflow that SSHes into the VM. This requires adding your `.pem` private key as a GitHub secret and using an action like `appleboy/ssh-action`. This is not currently set up in the repository.

---

## Updating the Frontend

Push to `main`. GitHub Actions automatically picks up the change, builds the Vite app, and deploys to Azure Static Web Apps. No manual steps needed.

Typical deploy time from push to live: 2–3 minutes. Monitor progress in the **Actions** tab on GitHub.

---

## Monitoring and Logs

### Container logs

```bash
# Follow live logs
sudo docker compose logs -f

# Last 100 lines only
sudo docker compose logs --tail=100

# Specific service
sudo docker compose logs api
```

### Nginx logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Container status

```bash
sudo docker compose ps
sudo docker stats
```

---

## Common Issues

**Health check returns FAISS index not found**

The FAISS index did not download from Blob on startup. Check:
- `AZURE_STORAGE_CONNECTION_STRING` is correct in `api/.env`
- `USE_LOCAL_FILES=false` in `api/.env`
- The blobs `data/faiss_store/legal_cases.index` and `data/faiss_store/id2name.json` exist in the storage account
- Check logs with `sudo docker compose logs api`

**Permission denied when copying files into `/opt/jurisfind`**

The directory is owned by root. Fix ownership:

```bash
sudo chown -R azureuser:azureuser /opt/jurisfind
```

**Port 80 not reachable from outside**

Check the VM's Network Security Group (NSG) in the Azure Portal. Under the VM → **Networking**, there must be an inbound rule allowing TCP port 80 from any source.

**GitHub Actions fails with missing API token**

The `AZURE_STATIC_WEB_APPS_API_TOKEN` secret is missing or wrong. Go to the Azure Portal → Static Web App → **Manage deployment token**, copy it, and update the GitHub secret.

**Frontend requests fail with CORS error**

The Static Web App URL is not in the `allow_origins` list in `api/main.py`. Add it, push to `main`, and run `git pull` + `docker compose up -d --build` on the VM.
