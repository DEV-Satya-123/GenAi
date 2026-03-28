#!/bin/bash

echo "🚀 Simple Docker Deploy"

# Check .env
if [ ! -f .env ]; then
    echo "❌ Create .env file with GEMINI_API_KEY=your_key"
    exit 1
fi

# Build and start
docker-compose up -d --build

echo "✅ Done!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "🌍 Nginx: http://localhost"