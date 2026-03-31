# AI Git Automation Agent

## Project Idea

An intelligent Git automation system that uses AI to streamline the Git workflow while maintaining human control. The system analyzes code changes, generates meaningful commit messages, scans for security vulnerabilities, and automates Git operations with human approval at critical decision points.

### Core Concept
Instead of developers manually writing commit messages and worrying about security issues, the AI agent:
- Reads your code changes (git diff)
- Understands what you changed and why
- Generates professional commit messages following conventions
- Scans for accidentally committed secrets or API keys
- Presents everything for your approval before committing
- Asks permission before pushing to remote

### Key Features
1. **AI-Powered Commit Messages** - Uses Google Gemini AI to generate contextual, conventional commit messages
2. **Security Scanning** - Integrates GitGuardian to detect secrets, API keys, and credentials before commits
3. **Human-in-the-Loop (HITL)** - Requires human approval before commits and pushes (not fully autonomous)
4. **Multi-Repository Management** - Clone, add, and switch between multiple Git repositories
5. **Real-Time Updates** - WebSocket-based live notifications and progress tracking

### Workflow
1. You make code changes in your repository
2. AI detects changes and analyzes the diff
3. Security scanner checks for sensitive data
4. AI generates a commit message
5. You review and approve/edit the message
6. Changes are committed locally
7. You approve pushing to remote
8. Changes are pushed to GitHub/GitLab

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Google Gemini AI** - LLM for commit message generation
- **GitPython** - Git operations wrapper
- **LangChain** - AI orchestration framework
- **Pydantic** - Data validation and settings
- **GitGuardian API** - Security scanning
- **WebSockets** - Real-time communication

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first styling
- **Socket.IO** - WebSocket client

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Uvicorn** - ASGI server

### AI/ML
- **Google Gemini 2.5 Flash Lite** - Fast, efficient LLM
- **Prompt Engineering** - Structured prompts for consistent output
- **JSON Parsing** - Structured AI responses

## Why This Project?

**Problem**: Developers spend time writing commit messages, worry about committing secrets, and repeat Git commands manually.

**Solution**: AI automates the tedious parts while humans maintain control over critical decisions.

**Benefit**: Faster workflow, better commit messages, improved security, reduced human error.

---

**Project Type**: HITL (Human-in-the-Loop) AI Agent  
**Status**: Beta - Functional with room for improvement  
**Rating**: 7.5/10
