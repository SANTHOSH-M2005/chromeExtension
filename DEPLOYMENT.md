# SmartConsent AI - Complete Production Deployment Guide

This guide covers how to deploy the entire **SmartConsent AI** system:
1. **Backend API (FastAPI + LangGraph + Chroma Vector DB)**: Containerized with Docker on any Linux VPS (DigitalOcean, AWS EC2, Linode, Hetzner, etc.) or local Docker server.
2. **Frontend Web App Preview**: Hosted as a standalone static web app on **Vercel** or **Netlify**.
3. **Chrome Extension**: Packed as a production archive (`.zip`) ready for Chrome Web Store submission or direct unpacked installation.

---

## Architecture Overview

```text
┌─────────────────────────────────┐        ┌──────────────────────────────────┐
│      Chrome Browser             │        │    Cloud Web Hosting (Vercel)    │
│  SmartConsent Side Panel (MV3)  │        │  Interactive Web Preview App     │
└───────────────┬─────────────────┘        └─────────────────┬────────────────┘
                │                                            │
                │  HTTPS / REST Calls (Configurable Endpoint)│
                ▼                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Self-Hosted VPS / Docker Host                         │
│                                                                             │
│  [ Optional Nginx Reverse Proxy with SSL (Certbot Let's Encrypt) ]          │
│                                │                                            │
│                                ▼ Port 8000                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     smartconsent-backend (Docker)                     │  │
│  │                                                                       │  │
│  │   • FastAPI ASGI Server (Uvicorn workers)                             │  │
│  │   • LangGraph Multi-Agent Privacy Analyzer                            │  │
│  │   • LangChain RAG & HuggingFace Embeddings (all-MiniLM-L6-v2)          │  │
│  │   • Chroma Vector DB (Indexed EU GDPR & India DPDP Legal Frameworks)  │  │
│  │   • SQLite / PostgreSQL Database                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│                 Persistent Volume: smartconsent-data                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Deploying Backend to Docker / Linux VPS / AWS EC2

### Prerequisites
- A Linux VPS (Ubuntu 22.04 / 24.04 or Debian recommended) or AWS EC2 instance.
- Port 80, 443 (HTTP/HTTPS) and optionally 8000 open in your security group / firewall (`ufw allow 8000`).

### Method A: Automated 1-Click Script (`deploy.sh`)
On your VPS terminal, simply run:
```bash
git clone <your-repo-url> smartconsent
cd smartconsent
chmod +x deploy.sh
./deploy.sh
```
The script will automatically install Docker & Docker Compose if missing, copy configuration, build the Docker container, index the RAG documents into Chroma DB, and start the service with a health check.

---

### Method B: Manual Docker Compose Deployment

#### 1. Configure Environment Variables
Inside `backend/.env` (or copy from `backend/.env.example`):
```env
PORT=8000
ALLOWED_ORIGINS=*,http://localhost:5173,https://your-preview-app.vercel.app

# Custom AI Provider
AI_API_KEY=your_actual_api_key_here
AI_BASE_URL=https://apidev.navigatelabsai.com/
AI_MODEL=gpt-4.1-nano

DATABASE_URL=sqlite:////app/data/smartconsent.db
CHROMA_DB_DIR=/app/data/chroma_db
RAG_DOCS_DIR=/app/rag/documents
```

#### 2. Start Services
From the project root:
```bash
docker compose up -d --build
```

#### 3. Verify Health
```bash
curl http://localhost:8000/health
```
Output:
```json
{"status":"healthy","service":"SmartConsent AI Backend"}
```

#### 4. Managing Containers
- **View Live Logs:**
  ```bash
  docker compose logs -f backend
  ```
- **Stop Containers:**
  ```bash
  docker compose down
  ```
- **Restart Container:**
  ```bash
  docker compose restart backend
  ```

---

### Setting up Nginx Reverse Proxy with HTTPS (Domain & SSL)

If you have a domain pointing to your VPS (e.g. `api.yourdomain.com`):

1. **Install Nginx & Certbot**:
   ```bash
   sudo apt update
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```
2. **Copy Nginx Config**:
   ```bash
   sudo cp nginx.conf.example /etc/nginx/sites-available/smartconsent
   sudo sed -i 's/api.yourdomain.com/YOUR_ACTUAL_DOMAIN/g' /etc/nginx/sites-available/smartconsent
   sudo ln -s /etc/nginx/sites-available/smartconsent /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
3. **Generate Free SSL Certificate with Let's Encrypt**:
   ```bash
   sudo certbot --nginx -d YOUR_ACTUAL_DOMAIN
   ```
Now your backend API is accessible securely at `https://YOUR_ACTUAL_DOMAIN`!

---

## Part 2: Deploying Frontend as a Web App Preview (Vercel / Netlify)

The SmartConsent UI is equipped with **dual-mode capability**:
- Inside Chrome: operates as a full-featured Manifest V3 SidePanel scanning active tabs.
- In Standard Browser (Vercel / Netlify): automatically activates **Web Preview Mode**, allowing users to paste any Terms of Service text or enter URLs for live AI analysis.

### Deploying to Vercel

1. Push your code to GitHub.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Select your repository.
4. Set the **Root Directory** to `extension`.
5. In **Build & Output Settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. In **Environment Variables**, add:
   - `VITE_API_URL`: Your deployed backend URL (e.g., `https://api.yourdomain.com` or `http://<YOUR_VPS_IP>:8000`).
7. Click **Deploy**.

> **Note**: `extension/vercel.json` is already configured with SPA route rewriting.

### Deploying to Netlify

1. Go to [netlify.com](https://netlify.com) and import your Git repository.
2. In **Build Settings**:
   - Base directory: `extension`
   - Build command: `npm run build`
   - Publish directory: `extension/dist`
3. In **Environment Variables**, set:
   - `VITE_API_URL` = `https://api.yourdomain.com`
4. Click **Deploy**.

---

## Part 3: Building & Distributing the Chrome Extension

### Option 1: Load Unpacked in Developer Mode (Local / Testing)
1. In the `extension` folder, run:
   ```bash
   npm run build
   ```
2. Open Google Chrome, Brave, or Microsoft Edge.
3. Navigate to `chrome://extensions/` (or `edge://extensions/`).
4. Toggle on **Developer mode** (top right switch).
5. Click **"Load unpacked"** (top left).
6. Select the `extension/dist` folder.
7. Click the SmartConsent AI extension icon in your browser toolbar or side panel!

---

### Option 2: Package ZIP for Chrome Web Store

To generate a clean production zip for publication to the Chrome Web Store:
1. Run:
   ```bash
   cd extension
   npm run pack
   ```
2. This runs the build and packages everything into:
   ```
   extension/smartconsent-extension.zip
   ```
3. Upload `smartconsent-extension.zip` directly to the [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole).

---

## Part 4: Dynamic In-App Backend Switching

Users don't need to recompile the extension or web preview when switching servers:

1. Open SmartConsent AI.
2. Click the **Settings** tab.
3. Under **Backend Server Endpoint**:
   - Enter your VPS URL (e.g., `http://192.168.1.50:8000` or `https://api.yourdomain.com`).
   - Click **"Test Connection"** to verify that the backend is online and reachable.
   - Click **"Save"**.
4. The extension immediately directs all clause extraction and chat requests to that server!
