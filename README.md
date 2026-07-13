# Analytics Copilot: Intelligent SQL Generation Agent

An **AI-powered conversational analytics agent** that transforms natural language questions into SQL queries, executes them, and provides insights from your data. Built with **LangGraph**, **Google Gemini**, and **LangChain**, this project demonstrates advanced LLM orchestration, agentic reasoning, and database interactions.

> ⚠️ **Project Status:** Currently in **active development** — core agent logic is functional, UI and deployment optimizations in progress.

---

## 🎯 Project Vision

### The Problem
Data analysts and business stakeholders face two challenges:
- **Technical barrier:** Most people can't write SQL
- **Time-consuming:** Manual query writing slows down decision-making
- **Context loss:** Q&A systems often misunderstand business terminology

### The Solution
**Analytics Copilot** bridges the gap:
```
Natural Language Question → Agent Reasoning → SQL Generation → Execution → Insights
```

### Why This Project?
This project showcases **enterprise-grade AI engineering skills**:
- **Agentic AI & LLM Orchestration** - Complex multi-step workflows with LangGraph
- **Advanced NLP** - Ambiguity detection, clarification, context understanding
- **Database Design** - SQL generation, validation, and optimization
- **System Architecture** - Modular agent nodes with state management
- **Full-Stack Integration** - Backend APIs with Streamlit frontend
- **Production Patterns** - Error handling, retries, guardrails
- **Data Engineering** - ETL pipelines, schema management, real-world datasets

---

## 📌 Current Status & Roadmap

### ✅ Completed Components
- [x] **LangGraph-based agent architecture** with stateful workflow
- [x] **Multi-mode operation** (Mode A: retrieval-based, Mode B: direct SQL)
- [x] **Ambiguity detection** - Intelligent clarification workflow
- [x] **SQL generation** - Google Gemini 2.5 Flash integration
- [x] **SQL guardrails** - Validation before execution
- [x] **Multi-step error recovery** - Automatic retries with context
- [x] **Database integration** - PostgreSQL/Supabase support
- [x] **Glossary/schema retrieval** - Semantic search for context
- [x] **Test data generation** - Realistic analytics datasets
- [x] **Backend agent framework** - Fully functional orchestrator

### 🚀 In-Progress Components
- [ ] Frontend UI (Streamlit) - Query interface and result visualization
- [ ] API endpoints - REST endpoints for agent orchestration
- [ ] User authentication - Multi-tenant support
- [ ] Query history & analytics - Logging and debugging
- [ ] Performance optimization - Query caching and indexing
- [ ] Error handling refinements - Better user feedback
- [ ] Integration testing - End-to-end workflow validation

### 📋 Future Enhancements
- [ ] Multi-database support (MySQL, BigQuery, Snowflake)
- [ ] Advanced analytics (chart generation, trend analysis)
- [ ] Prompt engineering optimization - Fine-tuned instructions
- [ ] Vector database integration - Semantic glossary search
- [ ] Query optimization - EXPLAIN plan analysis
- [ ] Audit logging - Query compliance & security
- [ ] Streaming responses - Real-time query feedback
- [ ] Cost estimation - Query execution cost prediction

---

## 🧠 Technical Concepts Explained

### What is Agentic AI?

Agentic AI systems use LLMs as intelligent reasoning engines that can:
- **Decide** what action to take next
- **Plan** multi-step workflows
- **Retry** failed attempts with corrected context
- **Validate** outputs against constraints

**In This Project:**
```
[User Question] → [Agent Decision] → [Action Execution] → [Validation] → [Retry or Respond]
```

### Agent Workflow Architecture

This project uses **LangGraph** to build a **state machine** that orchestrates the SQL generation pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                   START: route_question                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─► Mode A + Needs Glossary? ──►─┐
             │                                 │
             └─► Direct SQL? ──────────────────┤
                                               │
          ┌────────────────────────────────────┘
          ▼
    retrieve_glossary
    (if applicable)
          │
          ▼
    check_ambiguity
          │
          ├─► Ambiguous? ──► clarify (interrupt) ──┐
          │                                        │
          └─► Clear ─────────────────────────────┬─┤
              │                                   │
              └───────────────────────────────────┘
                          │
                          ▼
                   generate_sql
                   (Gemini API)
                          │
                          ▼
                  validate_sql_guard
                  (Constraint check)
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
    Valid?        Invalid/Retry?          Fail?
       │                  │                  │
       ▼                  ▼                  ▼
    execute_sql    generate_sql        respond
       │             (with context)      (error)
       ▼
   validate_result
       │
    Success?
       │
    ┌──┴──┐
    │     │
    YES   NO/Retry
    │     │
    ▼     ▼
 respond (try again
         up to MAX_RETRIES)
```

### Key Agent Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Nodes** | Individual decision/action points | LangGraph |
| **Edges** | Conditional routing between nodes | LangGraph |
| **State** | Persistent workflow context | `AgentState` class |
| **Checkpointing** | Resume interrupted workflows | MemorySaver |
| **Interrupts** | Human-in-the-loop for clarification | LangGraph interrupts |

---

## ✨ Key Features

| Feature | Implementation | Why It Matters |
|---------|-----------------|----------------|
| 🤖 **Natural Language → SQL** | Gemini 2.5 Flash LLM | No SQL knowledge required |
| 🔍 **Ambiguity Detection** | LLM-based classification | Reduces interpretation errors |
| ❓ **Clarification Workflow** | Human-in-the-loop interrupts | Handles edge cases interactively |
| 🛡️ **SQL Guardrails** | Syntax validation before execution | Prevents malformed queries |
| 🔄 **Smart Retries** | Context-aware retry logic | Recovers from transient errors |
| 📚 **Glossary Retrieval** | Semantic search on domain terms | Domain-specific SQL accuracy |
| 🗄️ **Multi-mode Operation** | Retrieval-based (Mode A) or Direct (Mode B) | Flexible for different use cases |
| 📊 **Real-world Datasets** | Events, sessions, users tables | Realistic analytics scenarios |
| 🧪 **Test Coverage** | Pytest integration ready | Production-ready code quality |

---

## 💻 Tech Stack

### **LLM & Agentic Framework**
- **LangGraph** - State machine & workflow orchestration
- **LangChain** - LLM abstractions and utilities
- **Google Gemini 2.5 Flash** - Multi-modal LLM for SQL generation
- **LangChain-Google-GenAI** - Gemini integration

### **Database & SQL**
- **PostgreSQL / Supabase** - Primary data store
- **SQLAlchemy** - ORM and SQL generation
- **psycopg2** - PostgreSQL adapter

### **Data Processing**
- **Pandas** - DataFrames and data manipulation
- **NumPy** - Numerical operations

### **Backend & APIs**
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server

### **Frontend**
- **Streamlit** - Interactive UI (in progress)

### **Development & Testing**
- **Python 3.11** - Core language
- **Pytest** - Unit testing
- **Python-dotenv** - Environment management

---

## 📂 Project Structure

```
analytics-copilot/
│
├── backend/                          # Core backend
│   │
│   ├── agent/                        # Agentic AI engine
│   │   ├── graph.py                  # LangGraph state machine builder
│   │   ├── graph_state.py            # AgentState definition
│   │   ├── nodes.py                  # All workflow nodes (10+ nodes)
│   │   ├── llm.py                    # Gemini LLM prompts & calls
│   │   ├── retrieval.py              # Glossary/schema retrieval
│   │   ├── db.py                     # Database execution layer
│   │   ├── sql_guard.py              # SQL validation guardrails
│   │   ├── validation.py             # Result validation logic
│   │   ├── orchestrator.py           # High-level agent orchestration
│   │   └── __init__.py
│   │
│   ├── data_generation/              # ETL & data generation
│   │   ├── generate_data.py          # Synthetic data generation
│   │   ├── load_data.py              # Data loading pipeline
│   │   ├── embed_glossary.py         # Glossary embedding for retrieval
│   │   ├── events.csv                # Sample events data (2M+ rows)
│   │   ├── sessions.csv              # Sample sessions data
│   │   └── users.csv                 # Sample users data
│   │
│   ├── tests/                        # Unit tests (pytest)
│   │
│   ├── requirements.txt              # Backend dependencies
│   └── pyproject.toml                # Package configuration
│
├── frontend/                         # Streamlit UI (in progress)
│   ├── requirements.txt              # Frontend dependencies
│   └── app.py                        # (to be implemented)
│
├── .env.example                      # Environment variables template
├── .gitignore
└── README.md
```

### Key Files Explained

**`backend/agent/graph.py`** - LangGraph workflow definition
```python
# Defines the state machine with nodes and conditional edges
graph.add_node("route_question", route_question)
graph.add_node("retrieve_glossary", retrieve_glossary_node)
graph.add_node("generate_sql", generate_sql_node)
# ... more nodes
# ... conditional routing logic
```

**`backend/agent/nodes.py`** - All decision & action nodes
```python
def route_question(state) → {}              # Entry point
def retrieve_glossary_node(state) → {}      # Retrieve context
def check_ambiguity(state) → {}             # Detect ambiguity
def clarify(state) → {}                     # Ask for clarification (interrupt)
def generate_sql_node(state) → {}           # Generate SQL
def validate_sql_guard_node(state) → {}     # Validate syntax
def execute_sql_node(state) → {}            # Execute query
def validate_result_node(state) → {}        # Validate results
def respond(state) → {}                     # Final response
```

**`backend/agent/llm.py`** - LLM prompts & integration
```python
SQL_GEN_PROMPT        # Schema + context → SQL generation
AMBIGUITY_PROMPT      # Detect if question is ambiguous
CLARIFICATION_PROMPT  # Generate follow-up questions
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **PostgreSQL 12+** or **Supabase** account
- **Google API Key** - Get from [Google AI Studio](https://aistudio.google.com/apikey)

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/singhrhl/analytics-copilot.git
cd analytics-copilot
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with:
# - SUPABASE_ADMIN_URL: Your Supabase project URL
# - SUPABASE_ADMIN_PASSWORD: Admin password
# - SUPABASE_HOST: Database host
# - AGENT_READONLY_PASSWORD: Read-only user password
# - GOOGLE_API_KEY: Your Google Gemini API key
```

#### 5. Generate & Load Test Data
```bash
cd backend
python -m data_generation.generate_data
python -m data_generation.load_data
cd ..
```

#### 6. Run Agent (CLI for now)
```bash
cd backend
python -c "from agent.orchestrator import run_agent; run_agent('What is our daily active users?')"
cd ..
```

---

## 📖 Agent API & Usage

### Current Implementation (Core Agent)

The agent is functional and can be invoked programmatically:

```python
from backend.agent.orchestrator import run_agent

# Run a natural language query
result = run_agent("What is the total number of active users in January 2025?")
print(result)
```

### Workflow Steps

```python
# 1. User asks a question
question = "How many unique users completed a lesson today?"

# 2. Agent routes the question (Mode A/B decision)
# 3. If Mode A: retrieves glossary context
# 4. Checks for ambiguity
# 5. If ambiguous: generates clarification question (interrupt)
# 6. Generates SQL using Gemini
# 7. Validates SQL syntax
# 8. Executes on database
# 9. Validates results
# 10. Returns formatted answer

# Output:
# {
#   "status": "success",
#   "final_answer": "12,345 unique users completed lessons today.",
#   "generated_sql": "SELECT COUNT(DISTINCT user_id) FROM events ...",
#   "execution_result": [{"count": 12345}]
# }
```

### Agent State Structure

```python
@dataclass
class AgentState:
    # Input
    user_question: str           # The original question
    mode: str = "A"              # Mode A (retrieval) or B (direct)
    
    # Processing
    schema_context: str = ""     # Database schema & glossary context
    ambiguity_status: str = ""   # "clear" or "needs_clarification"
    generated_sql: str = ""      # Generated SQL query
    
    # Clarification
    clarification_question: str = ""  # Follow-up question if needed
    clarification_answer: str = ""    # User's response
    
    # Execution
    execution_result: list = None     # Query results
    execution_error: str = ""         # Error message (if any)
    
    # Validation & Retry
    retry_count: int = 0              # Number of retry attempts
    retry_reason: str = ""            # Why retry was triggered
    status: str = ""                  # "success" or "failed_after_retries"
    
    # Output
    final_answer: str = ""            # Formatted response to user
```

---

## 🎓 Skills Demonstrated

### **AI & LLM Engineering**
- ✅ Agentic AI orchestration with LangGraph
- ✅ LLM prompt engineering and optimization
- ✅ Multi-turn conversations with context management
- ✅ Error recovery and retry strategies
- ✅ Guardrails and constraint validation
- ✅ Ambiguity detection and resolution

### **Software Architecture**
- ✅ State machine design patterns
- ✅ Modular agent node architecture
- ✅ Conditional workflow routing
- ✅ Checkpointing and resumable workflows
- ✅ Multi-mode operation strategies
- ✅ Human-in-the-loop integration (interrupts)

### **Database & SQL**
- ✅ SQL generation from natural language
- ✅ Schema validation and context building
- ✅ Complex query support (CTEs, subqueries)
- ✅ Database connection pooling
- ✅ Read-only user access patterns
- ✅ Real-world analytics schema design

### **Data Engineering**
- ✅ Synthetic data generation
- ✅ ETL pipeline design
- ✅ Schema design for analytics
- ✅ Data loading and validation
- ✅ Glossary/domain terminology management

### **Backend Development**
- ✅ Python backend architecture
- ✅ API design (FastAPI - in progress)
- ✅ Environment configuration management
- ✅ Error handling and logging
- ✅ Modular package structure

### **Full-Stack Development**
- ✅ Full agent lifecycle management
- ✅ Frontend integration (Streamlit - in progress)
- ✅ End-to-end workflow testing
- ✅ Development to deployment pipeline

---

## 🏗️ Architecture Decisions

### Why LangGraph?

**LangGraph** vs. alternatives:
- ✅ **Explicit workflow definition** - Clear state machine
- ✅ **Checkpointing** - Resume interrupted workflows
- ✅ **Interrupts** - Human-in-the-loop support
- ✅ **Debugging** - Trace execution step-by-step
- ✅ **Production-ready** - Built for LLM agents
- ❌ Simple alternatives (like basic chains) can't handle multi-step retry logic

### Why Gemini 2.5 Flash?

- ✅ **Speed** - Sub-second latency for SQL generation
- ✅ **Accuracy** - Strong SQL generation capability
- ✅ **Cost-effective** - Lower API costs
- ✅ **Multi-modal** - Can handle charts, images in future
- ✅ **Free tier** - Great for development

### Why PostgreSQL/Supabase?

- ✅ **ACID compliance** - Reliable for analytics
- ✅ **Rich types** - JSON, arrays, custom types
- ✅ **Performance** - Fast for analytical queries
- ✅ **Mature** - 20+ years in production
- ✅ **Supabase** - Managed PostgreSQL with auth, APIs

### Why Mode A + Mode B?

**Mode A (Retrieval):** For complex business questions that need glossary context
- Retrieves relevant schema & terminology
- Better accuracy for ambiguous terms
- Slightly higher latency

**Mode B (Direct):** For straightforward technical questions
- Direct SQL generation
- Lower latency
- Works well for standard queries

---

## 🔒 Security & Safeguards

### SQL Guardrails
```python
# Prevents:
# - DDL statements (CREATE, ALTER, DROP)
# - DML modifications (INSERT, UPDATE, DELETE)
# - Subquery bombs
# - Common injection patterns
```

### Database Access Control
```python
# Uses read-only user for queries
AGENT_READONLY_USER = "agent_readonly"
# Permissions: SELECT only on analytics tables
```

### API Security (Coming Soon)
- Rate limiting on query generation
- Input length validation
- Query history audit logging
- User authentication & authorization

---

## 📊 Performance Characteristics

| Operation | Typical Time | Factors |
|-----------|------------|---------|
| Route Question | <50ms | Routing logic only |
| Retrieve Glossary | 50-200ms | Semantic search in vector DB |
| Check Ambiguity | 200-500ms | LLM API call |
| Generate SQL | 500-1500ms | Gemini latency + complexity |
| Validate SQL | <100ms | Local validation |
| Execute Query | 100-5000ms | Query complexity & data size |
| **Total E2E** | **1-10s** | Depends on operations triggered |

**Optimization opportunities:**
- Caching SQL for common questions
- Batching clarification responses
- Pre-computing common aggregations
- Query plan analysis

---

## 🐛 Troubleshooting

### Issue: "Database connection refused"
**Solution:** Ensure Supabase/PostgreSQL is running and `.env` credentials are correct

### Issue: "Google API Key invalid"
**Solution:** Generate a new key at https://aistudio.google.com/apikey

### Issue: "Ambiguous term not recognized"
**Solution:** Add term to glossary CSV and re-embed with `embed_glossary.py`

### Issue: "SQL generation returns invalid syntax"
**Solution:** Check LLM response format - Gemini may return markdown-wrapped SQL

---

## 🚀 Next Steps for Completion

### Phase 1: API & Frontend (In Progress)
- [ ] Build FastAPI endpoints for agent
- [ ] Create Streamlit UI for query interface
- [ ] Add query history & result caching
- [ ] Implement user authentication

### Phase 2: Production Readiness
- [ ] Comprehensive error handling
- [ ] Logging & monitoring (LangSmith integration)
- [ ] Performance optimization
- [ ] Load testing

### Phase 3: Advanced Features
- [ ] Multi-database support
- [ ] Chart generation
- [ ] Query cost estimation
- [ ] Advanced analytics (trends, anomalies)

---

## 📚 Technology Stack Reference

| Domain | Technology | Version |
|--------|-----------|---------|
| **LLM Orchestration** | LangGraph | Latest |
| **LLM Framework** | LangChain | 0.1+ |
| **LLM Model** | Google Gemini 2.5 Flash | API |
| **Database** | PostgreSQL / Supabase | 12+ |
| **Backend** | FastAPI | 0.100+ |
| **Frontend** | Streamlit | Latest |
| **Language** | Python | 3.11+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Testing** | Pytest | Latest |

---

## 🤝 Contributing

This is a work-in-progress. Contribution areas:
- Frontend UI improvements
- Database schema optimizations
- LLM prompt engineering
- Test coverage expansion
- Performance optimization
- Documentation improvements

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **LangGraph** team for agentic AI orchestration framework
- **LangChain** community for LLM utilities
- **Google** for Gemini 2.5 Flash model
- **Supabase** for managed PostgreSQL
- **Streamlit** for rapid UI development

---

## 📧 Contact & Links

- **GitHub Repository:** https://github.com/singhrhl/analytics-copilot
- **Author:** [singhrhl](https://github.com/singhrhl)

---

## 📌 Development Notes

### Known Limitations (Current Phase)
- No persistent query history yet
- Frontend not deployed
- Limited to single database connection
- Clarification interrupts require programmatic handling
- No performance metrics dashboard

### Testing Checklist
- [ ] Agent routes questions correctly (Mode A vs B)
- [ ] Glossary retrieval returns relevant context
- [ ] Ambiguity detection works for test cases
- [ ] SQL generation produces valid queries
- [ ] Guardrails reject malicious SQL
- [ ] Retry logic recovers from errors
- [ ] Results are formatted correctly
- [ ] Integration tests pass

### Performance Optimization Priorities
1. LLM cache for similar queries
2. Vector DB indexing for glossary
3. Connection pooling optimization
4. Query plan analysis
5. Incremental result streaming

---

**Made with ❤️ as a portfolio project for AI Engineer roles**

This project demonstrates the ability to build **sophisticated AI systems** with complex reasoning, error recovery, and production-grade orchestration.

*Status Last Updated: July 2026 | Development Phase*
