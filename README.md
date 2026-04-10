# 🤖 AI Git Automation Agent

AI-powered Git automation with Google Gemini that generates commit messages and automates workflows with human approval.

## ✨ Features

- 🤖 AI-generated commit messages using Google Gemini
- 🔒 Security scanning with GitGuardian
- 👤 Human-in-the-loop approval workflow
- 🔐 JWT authentication
- 📊 Multi-repository management
- ⚡ Real-time WebSocket updates
- 🎨 React + TypeScript dashboard
- 🔍 **NEW:** Search commits by message/author
- 🛡️ **NEW:** Smart .gitignore auto-fix (detects & adds missing patterns)

## 🚀 Quick Start

1. **Setup environment:**
```bash
cd ai_git_agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure `.env`:**
```bash
GEMINI_API_KEY=your_key_here
GITGUARDIAN_API_KEY=your_key_here
JWT_SECRET_KEY=your_secret_here
```

3. **Run with Docker:**
```bash
docker-compose up --build
```

4. **Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🏗️ Architecture

```
Frontend (React + TypeScript)
    ↓ HTTP/WebSocket
Backend (FastAPI + Python)
    ↓
AI (Gemini) + Security (GitGuardian) + Git
```

## 🔄 Workflow

1. Detect code changes
2. Generate git diff
3. Security scan
4. AI generates commit message
5. Human approves/edits
6. Commit locally
7. Human approves push
8. Push to remote

## 📁 Structure

```
ai_git_agent/
├── backend/          # FastAPI server
├── frontend/         # React dashboard
├── llm/             # Gemini AI client
├── security/        # GitGuardian scanner
├── tools/           # Git operations
└── docker/          # Docker configs
```

## 📝 Technologies

- **Backend:** FastAPI, Python, JWT, WebSocket
- **Frontend:** React, TypeScript, TailwindCSS
- **AI:** Google Gemini 2.5 Flash Lite
- **Security:** GitGuardian, Rate Limiting
- **DevOps:** Docker, Nginx

## � ULicense

MIT License
