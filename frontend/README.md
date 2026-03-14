# AI Git Automation - Frontend

Professional dashboard for AI-powered Git automation with 3D workflow visualization.

## Features

- 🎨 Modern UI with Tailwind CSS
- 🎭 Smooth animations with Framer Motion
- 🌐 3D workflow graph with Three.js
- 📊 Real-time progress tracking
- 🔄 Live status updates
- 📡 WebSocket integration

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Three.js / React Three Fiber
- Socket.IO Client
- Axios

## Development

The frontend runs on `http://localhost:5173` and proxies API requests to the FastAPI backend on port 8000.

Make sure the backend is running before starting the frontend.
