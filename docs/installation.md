# Installation

## Prerequisites

- **Node.js**: 18.0+
- **Python**: 3.9+
- **Git**: Latest version
- **Groq API Key**: From [console.groq.com](https://console.groq.com/)

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Legal_Case
```

### 2. Backend Setup
```bash
cd api
python -m venv venv
# Activate venv (platform-specific)
pip install -r requirements.txt
cp .env.example .env
# Edit .env with GROQ_API_KEY
```

### 3. Generate Embeddings
```bash
python helpers/generate_embeddings.py
```

### 4. Start Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
# Access at http://localhost:5173
```

## Verification

- Backend: `curl http://localhost:8000/api/health`
- Frontend: Open browser to localhost:5173