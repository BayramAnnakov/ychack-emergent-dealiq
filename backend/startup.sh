#!/bin/bash
# Startup script to ensure appuser and Claude CLI are ready
# This runs automatically on container start

echo "🔧 Checking appuser and Claude CLI setup..."

# 1. Create appuser if doesn't exist
if ! id appuser &>/dev/null; then
    echo "Creating appuser..."
    useradd -m -s /bin/bash appuser
    echo "✅ appuser created"
else
    echo "✅ appuser already exists"
fi

# 2. Install Claude CLI for appuser if not installed
if [ ! -f "/home/appuser/node_modules/.bin/claude" ]; then
    echo "Installing Claude CLI for appuser..."
    su - appuser -c "npm install @anthropic-ai/claude-code" > /dev/null 2>&1
    echo "✅ Claude CLI installed"
else
    echo "✅ Claude CLI already installed"
fi

# 3. Set proper permissions
chown -R appuser:appuser /app/backend/data 2>/dev/null || true
chown -R appuser:appuser /app/backend/.claude 2>/dev/null || true
echo "✅ Permissions set"

# 4. Verify installation
if su - appuser -c "/home/appuser/node_modules/.bin/claude --version" > /dev/null 2>&1; then
    VERSION=$(su - appuser -c "/home/appuser/node_modules/.bin/claude --version")
    echo "✅ Claude CLI ready: $VERSION"
else
    echo "❌ Claude CLI verification failed"
    exit 1
fi

echo "🎉 Setup complete - ready for task execution!"
exit 0
