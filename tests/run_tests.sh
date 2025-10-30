#!/bin/bash

# Test runner for messaging system
# Usage: ./run_tests.sh

echo "🧪 Running Messaging System Tests..."
echo "===================================="
echo ""

cd ~/dev/repair_shop_api

# Install pytest if not already installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "📦 Installing pytest..."
    pip install pytest pytest-cov --break-system-packages
fi

echo ""
echo "Running tests..."
echo ""

# Run the tests with verbose output
pytest tests/test_messages.py -v --tb=short --color=yes

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Check output above."
fi

echo ""
echo "Run individual test: pytest tests/test_messages.py::test_send_message_success -v"
echo "Run with coverage: pytest tests/test_messages.py --cov=app/api/customers/messages"

exit $EXIT_CODE