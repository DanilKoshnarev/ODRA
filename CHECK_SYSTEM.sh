#!/bin/bash
# System status checker

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🔍 ODRA SYSTEM STATUS CHECK"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Backend
echo "📌 Backend API (Port 8000):"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ RUNNING"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "   Status: $(echo $HEALTH | grep -o '"status":"[^"]*' | cut -d'"' -f4)"
else
    echo "   ❌ NOT RUNNING"
fi
echo ""

# Check Frontend
echo "📌 Frontend Dev Server (Port 5173):"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ RUNNING"
else
    echo "   ❌ NOT RUNNING"
fi
echo ""

# Check Database
echo "📌 Database:"
if [ -f "odra.db" ]; then
    SIZE=$(du -h odra.db | cut -f1)
    echo "   ✅ EXISTS (Size: $SIZE)"
else
    echo "   ❌ NOT FOUND"
fi
echo ""

# Check Node modules
echo "📌 Frontend Dependencies:"
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ INSTALLED"
else
    echo "   ❌ NOT INSTALLED"
fi
echo ""

# Check Python venv
echo "📌 Python Virtual Environment:"
if [ -d ".venv" ]; then
    echo "   ✅ EXISTS"
else
    echo "   ❌ NOT CREATED"
fi
echo ""

# Check key files
echo "📌 Required Files:"
files=("backend/app/main.py" "frontend/src/App.tsx" "workers/processor.py" "init_db.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file"
    fi
done
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ STATUS CHECK COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""

