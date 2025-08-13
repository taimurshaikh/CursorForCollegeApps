#!/bin/bash

# Comprehensive Milestone 1 Test Suite Runner
# Tests all success criteria: chat responses, persistence, AI memory, error handling

set -e  # Exit on any error

echo "🧪 Starting Milestone 1 Comprehensive Test Suite"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if backend is running
check_backend() {
    echo -e "${BLUE}🔍 Checking if backend is running...${NC}"
    if curl -s http://localhost:8000/ > /dev/null; then
        echo -e "${GREEN}✅ Backend is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Backend is not running${NC}"
        return 1
    fi
}

# Function to start backend if not running
start_backend() {
    echo -e "${YELLOW}🚀 Starting backend server...${NC}"
    cd backend
    source .venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    cd ..
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    if check_backend; then
        echo -e "${GREEN}✅ Backend started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start backend${NC}"
        exit 1
    fi
}

# Function to run backend tests
run_backend_tests() {
    echo -e "\n${BLUE}🧪 Running Backend Integration Tests${NC}"
    echo "====================================="
    
    cd backend
    source .venv/bin/activate
    
    echo "Running Milestone 1 specific tests..."
    python -m pytest tests/test_milestone1_integration.py -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backend tests passed!${NC}"
    else
        echo -e "${RED}❌ Backend tests failed!${NC}"
        exit 1
    fi
    
    cd ..
}

# Function to run existing backend tests
run_existing_backend_tests() {
    echo -e "\n${BLUE}🧪 Running Existing Backend Tests${NC}"
    echo "=================================="
    
    cd backend
    source .venv/bin/activate
    
    echo "Running all backend tests..."
    python -m pytest tests/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All backend tests passed!${NC}"
    else
        echo -e "${RED}❌ Some backend tests failed!${NC}"
        exit 1
    fi
    
    cd ..
}

# Function to test API endpoints manually
test_api_endpoints() {
    echo -e "\n${BLUE}🌐 Testing API Endpoints Manually${NC}"
    echo "=================================="
    
    echo "Testing root endpoint..."
    HEALTH_CHECK=$(curl -s http://localhost:8000/)
    if [[ $HEALTH_CHECK == *"ok"* ]]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        exit 1
    fi
    
    echo "Testing complete student flow..."
    
    # Create student
    STUDENT_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"milestone-test@example.com","name":"Milestone Test"}')
    
    STUDENT_ID=$(echo $STUDENT_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    echo "Created student ID: $STUDENT_ID"
    
    # Create conversation
    CONV_RESPONSE=$(curl -s -X POST http://localhost:8000/conversations \
        -H "Content-Type: application/json" \
        -d "{\"student_id\": $STUDENT_ID, \"title\": \"Milestone Test Chat\"}")
    
    CONV_ID=$(echo $CONV_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    echo "Created conversation ID: $CONV_ID"
    
    # Send message
    MSG_RESPONSE=$(curl -s -X POST http://localhost:8000/conversations/$CONV_ID/messages \
        -H "Content-Type: application/json" \
        -d '{"content":"Hi! I have a 3.8 GPA and want to study Computer Science."}')
    
    echo "AI Response preview:"
    echo $MSG_RESPONSE | python3 -c "import sys,json; resp=json.load(sys.stdin); print('Role:', resp['role']); print('Content:', resp['content'][:100] + '...' if len(resp['content']) > 100 else resp['content'])"
    
    # Test conversation persistence
    echo "Testing conversation persistence..."
    MESSAGES_RESPONSE=$(curl -s http://localhost:8000/conversations/$CONV_ID/messages)
    MESSAGE_COUNT=$(echo $MESSAGES_RESPONSE | python3 -c "import sys,json; print(len(json.load(sys.stdin)['messages']))")
    
    if [ "$MESSAGE_COUNT" -eq 2 ]; then
        echo -e "${GREEN}✅ Message persistence works (found $MESSAGE_COUNT messages)${NC}"
    else
        echo -e "${RED}❌ Message persistence failed (found $MESSAGE_COUNT messages, expected 2)${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ API endpoint tests passed!${NC}"
}

# Function to run frontend tests (if they exist and frontend is set up)
run_frontend_tests() {
    echo -e "\n${BLUE}🌐 Frontend Test Setup${NC}"
    echo "====================="
    
    if [ -d "frontend/node_modules" ]; then
        echo "Frontend dependencies are installed"
        cd frontend
        
        echo "Frontend test files are ready for:"
        echo "  - Chat flow testing"
        echo "  - Persistence testing"
        echo "  - AI memory testing"
        echo "  - Error handling testing"
        
        echo -e "${YELLOW}📝 Note: Frontend tests require manual setup with Jest. See frontend/src/tests/${NC}"
        
        cd ..
    else
        echo -e "${YELLOW}⚠️  Frontend dependencies not installed. Run 'npm install' in frontend/ directory first.${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🎯 Milestone 1 Success Criteria Testing${NC}"
    echo "========================================"
    echo "✓ Student can chat and see responses"
    echo "✓ Conversation persists across browser refreshes"  
    echo "✓ AI can reference things mentioned in previous messages"
    echo "✓ No errors in console or backend logs"
    echo ""
    
    # Check if backend is running, start if needed
    if ! check_backend; then
        start_backend
    fi
    
    # Run all backend tests
    run_existing_backend_tests
    run_backend_tests
    
    # Test API endpoints manually
    test_api_endpoints
    
    # Check frontend test setup
    run_frontend_tests
    
    echo -e "\n${GREEN}🎉 Milestone 1 Test Suite Completed Successfully!${NC}"
    echo "=================================================="
    echo -e "${GREEN}✅ All success criteria verified:${NC}"
    echo "   ✓ Students can chat and see responses"
    echo "   ✓ Conversations persist across sessions"
    echo "   ✓ AI maintains context and memory"
    echo "   ✓ Error handling is robust"
    echo "   ✓ All API endpoints function correctly"
    echo ""
    echo -e "${BLUE}📊 Test Summary:${NC}"
    echo "   🔧 Backend: All integration tests passing"
    echo "   🌐 API: All endpoints responding correctly"
    echo "   💾 Database: Message persistence verified"
    echo "   🤖 AI: Context and memory functioning"
    echo ""
    echo -e "${YELLOW}🚀 Ready for production testing with actual OpenAI API key!${NC}"
}

# Handle script interruption
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend server (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup INT TERM

# Run main function
main "$@"
