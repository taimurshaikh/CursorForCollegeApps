# AI College Counseling Platform 🎓

A comprehensive AI-powered college counseling platform that helps students navigate their college application journey with personalized guidance, document management, and intelligent recommendations. The core vision is to be a one-stop-shop for all college application needs, and to have the chat UI be the main way to interact with the platform.

## 🚀 Project Overview

This platform is being built as a "cupcake version" - complete functionality with simplified implementation, designed to be expanded incrementally through well-defined milestones.

### Core Vision

- **Personalized Guidance**: AI-powered conversations that remember student context across sessions
- **Document Intelligence**: Upload and analyze college-related documents (transcripts, essays, etc.)
- **Proactive Assistance**: Smart suggestions based on student profile and goals, what you need, when you need it.
- **Natural Language Commands**: Intuitive interaction for scheduling, reminders, and planning

## 🏗️ Architecture

### Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python + SQLAlchemy + SQLite
- **AI**: OpenAI GPT-4o-mini with context management

### Project Structure

```
CursorForCollegeApps/
├── README.md                 # This file
├── run-milestone1-tests.sh   # Comprehensive test runner
├── frontend/                 # React application
│   ├── src/
│   │   ├── ui/App.tsx       # Main chat interface
│   │   └── lib/api.ts       # Backend API client
│   └── README.md            # Frontend setup guide
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── main.py          # API endpoints
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── ai.py            # OpenAI integration
│   │   └── settings.py      # Configuration
│   ├── tests/               # Comprehensive test suite
│   └── README.md            # Backend setup guide
```

## 🎯 Development Milestones

### ✅ Milestone 1: Basic Chat with Memory (COMPLETED)

**Goal**: Foundation chat system with persistent conversations and AI memory

**Features Implemented**:

- ✅ Student authentication (email-based login)
- ✅ Real-time chat interface with message history
- ✅ Conversation persistence across browser sessions
- ✅ AI context management (short-term: last 30 messages, long-term: summaries)
- ✅ Multiple conversation support
- ✅ Graceful error handling and logout functionality

**Success Criteria**:

- ✅ Student can chat and receive AI responses
- ✅ Conversations persist across browser refreshes
- ✅ AI references previous messages in conversations
- ✅ No console errors or backend failures
- ✅ Comprehensive test coverage (95%+ backend routes)

**Technical Implementation**:

- **Database Schema**: Students, conversations, messages, and student context tables
- **AI Memory System**:
  - Short-term: Last 30 messages per conversation
  - Long-term: AI-generated summaries updated every 6 messages
- **API Endpoints**: Auth, conversation management, message handling
- **Frontend State**: localStorage persistence, optimistic updates, error recovery

### 🔄 Milestone 2: Document Upload & Analysis (PLANNED)

**Goal**: Students can upload essays/documents, and AI can reference them in chat.

**Success Criteria**:

- Students can upload text files
- AI references appropriate documents in responses
- Documents show up in sidebar
- @references work in chat input

### 🔄 Milestone 3: Natural Language Commands

**Goal**: Chat-first interface for common actions using OpenAI function calling.

**Success Criteria**:
(Examples)

- "Update my GPA to 3.8" works
- "Add Stanford to my list" works
- Confirmations show in chat
- Data persists in database

### 🔄 Milestone 4: Proactive Suggestions (PLANNED)

**Goal**: AI-driven recommendations based on student profile, goals, and what they need. Heavily personalized.

**Implementation**:

- Daily background task that checks each student's status
- Simple rules-based suggestions (not complex AI reasoning yet)

- Store suggestions in database, show as notifications in UI
- Student can dismiss or act on suggestions

**Example Suggestions**:

- "You haven't worked on essays in 3 days—would you like some feedback or brainstorming help?"
- "Your college list only has reach schools—want to explore some target or safety options that match your interests?"
- "MIT's early deadline is in 2 weeks—would you like to review your application checklist or get tips for your essays?"
- "Based on your intended major, have you considered applying to schools with strong programs in Computer Science, like Carnegie Mellon or Georgia Tech?"
- "Your SAT score improved by 50 points since your last practice test—congratulations! Would you like to update your college list or set a new goal?"
- "You haven't scheduled any campus visits yet—would you like help finding virtual tours or planning a visit?"
- "Your Common App essay draft hasn't been updated in a week—need a reminder to work on it or want AI feedback?"
- "You mentioned an interest in environmental science—should I suggest some scholarship opportunities or summer programs?"
- "You have a recommendation letter deadline coming up in 5 days—do you want a checklist to make sure everything is ready?"

**Success Criteria**:

- Background job runs daily
- Relevant suggestions appear in UI
- Students can interact with suggestions
- No spam - max 1 suggestion per day per student

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd CursorForCollegeApps
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_key_here" > .env
echo "DATABASE_URL=sqlite:///backend/app.db" >> .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup (New Terminal)

```bash
cd frontend
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start frontend development server
npm run dev
```

### 4. Test the Application

- Open browser to `http://localhost:5173`
- Login with any email (e.g., `student@example.com`)
- Start chatting with the AI counselor!

### 5. Run Comprehensive Tests

```bash
# From project root
./run-milestone1-tests.sh
```

## 🧪 Testing Strategy

The project includes comprehensive testing at multiple levels:

- **Backend Integration Tests**: Full API endpoint coverage
- **AI Integration Tests**: OpenAI interaction validation
- **Database Tests**: Schema and relationship validation
- **Error Handling Tests**: Graceful failure scenarios
- **End-to-End Scenarios**: Complete user workflows

Test coverage includes:

- ✅ Authentication flows
- ✅ Conversation management
- ✅ Message handling with AI responses
- ✅ Student context summarization
- ✅ Error scenarios and edge cases
- ✅ Database persistence and retrieval

## 📝 Development Notes

### Key Design Decisions

1. **SQLite for Simplicity**: Easy development and deployment, can migrate to PostgreSQL later
2. **FastAPI for Speed**: Modern async Python framework with automatic API docs
3. **React + Vite**: Fast development with hot reloading and modern tooling
4. **OpenAI Integration**: Reliable AI responses with configurable models
5. **Incremental Architecture**: Built to expand - each milestone adds capabilities without breaking existing features

### Memory Management Strategy

The AI memory system is designed for scalability:

- **Recent Context**: Last 30 messages provide immediate conversation context
- **Summary Context**: AI-generated summaries capture long-term student information
- **Periodic Updates**: Summaries refresh every 6 messages to stay current
- **Cross-Conversation Memory**: Student context persists across all conversations

### Error Handling Philosophy

Robust error handling ensures a smooth user experience:

- **Graceful Degradation**: App continues working even if AI fails
- **User Feedback**: Clear error messages without technical details
- **State Recovery**: Automatic logout and recovery from invalid states
- **Optimistic Updates**: Immediate UI feedback with rollback on errors

## 🤝 Contributing

This project follows a milestone-driven development approach. Each milestone is self-contained and thoroughly tested before moving to the next phase.

### Development Workflow

1. Complete current milestone features
2. Achieve 100% success criteria
3. Run comprehensive test suite
4. Code review and documentation update
5. Git tag milestone completion
6. Plan next milestone features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Current Status**: Milestone 1 Complete ✅  
**Next Up**: Document Upload & Analysis  
**Last Updated**: Initial Implementation
