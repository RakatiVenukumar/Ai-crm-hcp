# AI-First CRM HCP Interaction Module

Production-ready AI-powered CRM workflow for pharmaceutical field representatives with natural language AI responses and automatic structured data extraction.

## What You Get

- **FastAPI backend** with SQLite persistence and database session injection
- **LangGraph agent** orchestration with multi-turn conversation memory
- **5 fully integrated tools**:
  - `LogInteractionTool` - persist interactions to database
  - `EditInteractionTool` - update existing records with partial edits
  - `InteractionSummaryTool` - generate professional summaries via Groq
  - `FollowupRecommendationTool` - create actionable next steps
  - `SalesInsightTool` - extract sentiment, objections, opportunities, product interest
- **React + Redux frontend** with persistent conversation history
- **Natural language AI responses** instead of raw JSON (human-friendly chat)
- **End-to-end workflow**:
  - Raw field notes → AI extraction → editable form → save → timeline
  - Multi-turn conversation context preserved across interactions
  - Automatic time extraction from user input (defaults to current time if omitted)
  - Correction mode for name-only fixes
  - Form reset when clearing conversation

## Key Features

### Frontend
- **Chat Panel** (55% width): AI conversation with natural language responses + conversation history
- **Interaction Form** (45% width): Auto-populated editable fields for all interaction details
- **Timeline** (bottom): Recent saved interactions for quick reference
- **Smart Auto-fill**: AI extracts HCP name, sentiment, products, time, attendees, materials, samples, outcomes, follow-up actions, and summary
- **Time Extraction**: If user mentions time (e.g., "3:30 PM", "afternoon", "10 AM"), AI extracts and populates time field; otherwise uses current time
- **Correction Mode**: Detects patterns like "sorry the name is Dr. Venu not Dr. Patel" and updates only the HCP name field, preserving other extracted data
- **Conversation Memory**: All messages persist until user deletes chat (also clears form)
- **Manual Editing**: Every AI-filled field can be manually overridden before saving

### Backend
- **LangGraph Agent**: 4-node workflow (agent → router → tool executor → finalize)
- **Multi-turn Context**: Conversation history passed to agent for coherent follow-ups
- **Database Session Injection**: Tools receive SQLAlchemy sessions via dependency injection
- **Natural Response Generation**: `generate_response_message()` creates conversational acknowledgments like "✓ Recorded: Dr. Venu - Sentiment: Positive. Discussed CardioCare. Next step: Send product documentation..."
- **Smart LLM Prompts**: 
  - Time extraction with format normalization (HH:MM 24-hour)
  - Guaranteed follow_up_recommendation for positive/neutral sentiment (with smart fallback)
  - Safe JSON parsing with error recovery
- **Tool Queue**: Router supports sequential tool execution (e.g., log → summarize → followup → sales_insight)
- **Error Resilience**: Graceful handling of missing required fields, empty input, API failures

## Project Structure & Architecture

### File Organization

```text
Ai-crm-hcp/
  backend/
    app/
      agents/          # LangGraph agent, state, node logic
      database/        # SQLAlchemy ORM, session management
      models/          # HCP, Interaction models
      routes/          # API endpoints (agent, hcp, interaction)
      schemas/         # Pydantic request/response models
      services/        # Groq LLM service, business logic
      tools/           # 5 execution tools (log, edit, summary, followup, insight)
      main.py          # FastAPI app, startup, route registration
    requirements.txt
    test_step*.py      # Test scripts for each tool
  frontend/
    src/
      components/      # AgentChatPanel, InteractionEditor, RecentTimeline
      pages/           # LogInteractionScreen (main orchestrator)
      redux/           # Redux slices (agentSlice, hcpSlice, interactionSlice)
      services/        # API client, HCP service, agent service
      styles.css       # Layout grid, component styling
    package.json
```

### Data Flow

**User Input → AI Analysis → Form Auto-fill → Save → Timeline:**

```
Frontend (React)
    ↓
Redux dispatch runAgentChat(userInput, conversationHistory)
    ↓
agentService.chat() POST /agent/chat
    ↓
FastAPI agent_routes.py
    ↓
CRMAgent.process_input()
    ↓
LangGraph nodes:
  - agent_node (Groq extraction)
  - router_node (decide tool)
  - tool_executor_node (run tool)
  - finalize_node (format response)
    ↓
response_message + extracted_data
    ↓
Redux stores in conversationHistory
Redux updates lastResponse for form
    ↓
Form auto-populates from extracted_data
    ↓
User saves → InteractionService.create()
    ↓
Timeline updated
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm 9+
- Groq API key (optional for non-LLM API checks, required for AI responses)

## Backend Setup

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with your key:

```env
GROQ_API_KEY=your_real_key_here
```

Run backend:

```powershell
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## Frontend Setup

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL:

- App: `http://localhost:5173/`

## Environment Files

### backend/.env

```env
ENV=development
HOST=0.0.0.0
PORT=8000
RELOAD=true
DATABASE_URL=sqlite:///./crm.db
GROQ_API_KEY=your_real_key_here
LOG_LEVEL=INFO
```

### frontend/.env

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints

### Agent Chat (Primary Endpoint)

**POST /agent/chat**
```json
Request:
{
  "user_input": "Met Dr. Chen this afternoon at 3:30 PM, discussed CardioCare, positive response",
  "conversation_history": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ]
}

Response:
{
  "success": true,
  "user_input": "Met Dr. Chen...",
  "extracted_data": {
    "hcp_name": "Dr. Chen",
    "sentiment": "positive",
    "products_discussed": ["CardioCare"],
    "time": "15:30",
    "attendees": "Not specified",
    "materials_shared": "Not specified",
    "samples_distributed": "Not specified",
    "outcomes": "Not specified",
    "follow_up_recommendation": "Send product documentation and schedule follow-up call",
    "summary": "Positive meeting discussing cardioCare system..."
  },
  "response_message": "✓ Recorded: Dr. Chen - Sentiment: Positive. Discussed CardioCare. Next step: Send product documentation and schedule follow-up call",
  "tool_results": {
    "last_result": {"success": true, "message": "..."}
  },
  "reasoning": "Successfully extracted HCP interaction data",
  "complete": true,
  "error": null
}
```

**GET /agent/health**
Returns agent status and available tools list.

### HCP Management

- `POST /hcp` - Create HCP
- `GET /hcp` - List all HCPs
- `GET /hcp/{hcp_id}` - Get single HCP
- `PUT /hcp/{hcp_id}` - Update HCP
- `DELETE /hcp/{hcp_id}` - Delete HCP

### Interactions

- `POST /interaction/log` - Save new interaction
- `POST /interaction/edit/{interaction_id}` - Update interaction
- `GET /interaction/timeline` - Get recent interactions
- `GET /interaction/{hcp_id}` - Get HCP-specific interactions

## Quick Demo Flow

1. **Start backend**:
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```
2. **Start frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
3. **Open frontend**: `http://localhost:5173`
4. **Paste raw interaction notes** in chat panel:
   ```
   Met Dr. Chen this afternoon at 3:30 PM. Discussed CardioCare and heart monitoring.
   Attendees: Dr. Chen and two nurses. Shared product brochures and left 2 trial samples.
   Very positive reception. She wants follow-up training session next week.
   ```
5. **Click "Analyze with AI"**:
   - AI responds in natural language: "✓ Recorded: Dr. Chen - Sentiment: Positive..."
   - Form auto-fills with extracted HCP, time (15:30), sentiment, materials, samples, outcomes, follow-up
6. **Review auto-filled fields** in Interaction Record panel
7. **Optionally edit any field** (all fields are editable)
8. **Click "Save Interaction"**
9. **Verify in Timeline** that interaction appears with saved details

### Multi-turn Example (Conversation Memory)

1. First message: "Meeting with Dr. Smith about products X and Y"
2. AI responds and fills form
3. Second message: "Actually, the name is Dr. Patel not Smith"
4. AI detects correction pattern and updates only the HCP name → Dr. Patel
5. All other fields (products, sentiment, etc.) remain intact
6. Save once complete

## Task 1 Learning: Architecture & Design Decisions

### Key Insights from Development

**1. AI Extraction Needs Deterministic Execution**
- Just LLM prompts aren't enough; reliable systems need tool execution
- Each tool handles a specific concern: persistence, editing, analysis, recommendations
- Tools can be tested independently with test_step scripts

**2. Separation of Concerns**
- Routes (REST contract) → Agent (reasoning/routing) → Tools (actions) → Services (LLM/DB)
- Makes code testable, debuggable, and maintainable
- Easy to add new tools without touching agent logic

**3. Conversation Context Matters**
- Without history, follow-ups and corrections lose meaning
- Redux persists conversation in frontend for multi-turn workflows
- Agent receives full history to make intelligent routing decisions

**4. User Control > Pure Automation**
- AI auto-fills everything, but user must retain manual override ability
- Before-save editing ensures user trust and data quality
- Correction mode preserves extracted data when user fixes only one field

**5. Error Handling & Defaults Are Production Requirements**
- Time fallback: If no time mentioned, use current time
- Follow-up fallback: If LLM returns empty for positive sentiment, provide smart default
- JSON parsing robustness: Extract text from malformed LLM responses
- Validation: Required fields checked early to fail fast

**6. Response Format Affects UX**
- JSON response was technically correct but not user-friendly
- Converting to natural text (`response_message`) improved adoption
- Users see conversational acknowledgment: "✓ Recorded: Dr. Chen..."

**7. LangGraph Clarifies Multi-Step Workflows**
- Instead of monolithic agent function, explicit nodes for readability
- Conditional routing (router → tool or finalize) is intuitive
- Tool queue enables sequential execution (log → summarize → followup)

### Production Considerations

- **Database sessions**: Injected via FastAPI dependencies for clean resource management
- **API contracts**: Pydantic schemas enforce request/response structure
- **Logging**: Structured logging at each node for debugging agent behavior
- **Type hints**: Python type hints catch bugs before runtime
- **Test coverage**: Each tool and agent flow validated with standalone tests

## Running Tests

Validate individual tools:

```powershell
cd backend

# Test LogInteractionTool (database persistence)
python test_step9_tool.py

# Test EditInteractionTool (updates)
python test_step10_tool.py

# Test InteractionSummaryTool (LLM summaries)
python test_step11_tool.py

# Test FollowupRecommendationTool (next steps)
python test_step12_tool.py

# Test SalesInsightTool (sentiment/opportunities)
python test_step13_tool.py

# Test Agent + Tools integration
python test_step14_agent.py

# Test API endpoint
python test_step15_agent_api.py
```

All tests should output `[OK]` status lines and finish with `ALL TESTS PASSED`.

## Troubleshooting (Windows)

You ran npm from the wrong directory.

Use:

```powershell
npm --prefix C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\frontend run dev
```

### `venv\Scripts\python.exe is not recognized`

You are not inside `backend`.

Use full path or change directory first:

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\backend
.\venv\Scripts\python.exe test_step14_agent.py
```

### Agent returns key/config errors

Set `GROQ_API_KEY` in `backend/.env` and restart backend.

## Development Notes

- **DB file**: `backend/crm.db` (SQLite, auto-created on startup)
- **Frontend API base**: Uses `VITE_API_BASE_URL` from `.env` (default: `http://127.0.0.1:8000`)
- **CORS**: Enabled for local development (allow_origins=["*"])
- **Hot reload**: Both backend (uvicorn --reload) and frontend (Vite HMR) support live changes
- **Logging**: Structured logging shows agent flow, LLM calls, tool execution
- **Groq API**: Required for LLM features; tests gracefully handle missing key with Skip status
- **Redux DevTools**: Can be installed for debugging state changes in frontend

## Project Evolution & Latest Updates

### Core Implementation (Steps 1-15)
Completed backend foundation with all 5 tools and API layer.

### Latest Enhancements (Recent Commits)

✅ **Groq Model Stabilization**
- Fixed deprecated models (gemma2-9b-it, mixtral-8x7b-32768)
- Using production model: `llama-3.3-70b-versatile`

✅ **Natural Language AI Responses**
- Replaced JSON response display with conversational text
- `response_message` field: "✓ Recorded: Dr. Venu - Sentiment: Positive. Discussed CardioCare. Next step: ..."
- Backend: `groq_service.generate_response_message(extracted_data, is_correction)`
- Frontend: Redux stores and displays `response_message` in chat

✅ **Time Extraction & Smart Fallback**
- LLM extracts time mentions: "afternoon" → 14:00, "3:30 PM" → 15:30
- Frontend `parseTimePhrase()` handles regex patterns and 24-hour conversion
- Fallback: If no time mentioned, uses current time
- Format validation: HH:MM stored in database

✅ **Conversation History & Multi-turn Context**
- Frontend Redux `conversationHistory` array preserves all messages with timestamps
- Backend receives history in `/agent/chat` request
- LangGraph agent includes history for coherent context
- User can delete entire conversation (also clears form state)

✅ **Correction Mode Detection**
- Pattern: "Sorry the name is Dr. Venu not Dr. Patel"
- Detection keywords: 2+ of [sorry, correction, name, not, actually, oops]
- Behavior: Only updates HCP name field, preserves other extracted data
- Example: "sentiment: positive, products: [A, B]" unchanged

✅ **Form Reset on Chat Delete**
- `handleClearHistory()` clears conversation + form state
- Form returns to initial state with empty fields
- Ensures fresh start after deleting dialogue

✅ **Database Session Injection**
- FastAPI dependency: `db: Session = Depends(get_db)`
- Passed through agent state to all tool executors
- Fixed tool execution errors ("missing 1 required positional argument: 'db'")

✅ **Enhanced LLM Prompts**
- Follow-up extraction: Guaranteed non-null for positive/neutral sentiment
- Fallback: "Send product documentation and schedule follow-up call"
- Safe JSON parsing with error recovery

✅ **Optimized UI Layout**
- Grid: 1.2fr 1fr (55% chat, 45% form)
- Independent scrolling for each panel
- Compact fonts (11-12px) and padding
- Max viewport height: 80vh with proper overflow handling

### Test Coverage
All 5 tools validated with test scripts:
- `test_step9_tool.py` - LogInteractionTool (persistence)
- `test_step10_tool.py` - EditInteractionTool (updates)
- `test_step11_tool.py` - InteractionSummaryTool (LLM summaries)
- `test_step12_tool.py` - FollowupRecommendationTool (next steps)
- `test_step13_tool.py` - SalesInsightTool (sentiment/opportunities)
- `test_step14_agent.py` - Agent + tool integration
- `test_step15_agent_api.py` - API endpoint validation

### Current Status
✅ **Production Ready**
- Backend: All endpoints functional, error handling, database persistence
- Frontend: Full UI workflow, form auto-fill, conversation memory, manual editing
- Integration: Seamless frontend-to-backend flow with natural responses
- Architecture: Clean separation of concerns (routes → agent → tools → services)
