# Enterprise HR Policy & Employee Support Agentic RAG Copilot

 An end-to-end **Forward Deployed Engineer (FDE)** project that transforms an Agentic RAG workflow into a deployable internal HR product using **LangGraph, FastAPI, Pinecone, Groq, Hugging Face Embeddings, Tavily, HTML, CSS, and JavaScript**.

 The system provides employees with grounded answers to HR policy questions by prioritizing the company's private HR knowledge base and using web search only when internal evidence is insufficient.

---

 ## 1\. Business Problem

 ### Customer

 **NovaRetail**, a fictional 3,000-employee retail company.

 ### Problem

 The HR team maintains many internal documents, including:

 - Leave and vacation policies
- Remote-work rules
- Payroll guidance
- Benefits information
- Employee onboarding procedures
- Code of conduct policies
- HR operations runbooks

 Employees still ask repetitive HR questions because:

 - They do not know where the correct policy is located.
- Traditional keyword search can return too many irrelevant documents.
- Generic chatbots may hallucinate or invent policy details.
- Internal documents may not contain current public information.
- Some questions require fresh external information.

 ### Example 1 — Private Company Policy

 An employee asks:

 > "How many annual leave days do employees receive?"

 The answer exists in the company's private HR knowledge base.

 The system should answer using the internal HR documents without searching the public internet.

 ### Example 2 — Current External Information

 Another employee asks:

 > "What are the latest public holiday rules in Bangladesh?"

 The internal HR knowledge base may not contain current public information.

 The system should:

 1. Search the private HR knowledge base first.
2. Determine whether the retrieved evidence is sufficient.
3. Fall back to web search if the private evidence is insufficient.
4. Evaluate the external evidence.
5. Generate an answer clearly identified as external information that may require HR validation.

 ### Business Goal

 Build a secure HR Policy Copilot that:

 1. Searches trusted private HR knowledge first.
2. Evaluates whether retrieved evidence is sufficient.
3. Uses web search only when private knowledge is insufficient.
4. Rewrites weak or ambiguous queries and retries retrieval.
5. Generates grounded answers based on retrieved evidence.
6. Shows the LangGraph decision path for transparency and debugging.
7. Allows authorized HR staff to add new company documents.
8. Maintains an audit trail of agent decisions.

---

 ## 2\. Why This Is an FDE Project

 A Forward Deployed Engineer does more than build an LLM prototype or notebook.

 The FDE translates a real customer problem into a usable, deployable product:

```
Customer Problem
      ↓
Discovery & Requirements
      ↓
Solution Architecture
      ↓
Data / Knowledge Integration
      ↓
Agentic RAG Development
      ↓
API Development
      ↓
User Interface
      ↓
Security + Audit + Testing
      ↓
Deployment
      ↓
Observe + Improve
```

 This project demonstrates that complete lifecycle:

 - Business problem definition
- Agent architecture
- Private knowledge integration
- Vector search
- LLM orchestration
- External search fallback
- API development
- Frontend development
- Document ingestion
- Audit logging
- Dockerization
- Production-oriented configuration

---

 ## 3\. System Architecture

```
                    Employee / HR User
                           │
                           ▼
                  HTML / CSS / JavaScript
                           │
                           │ POST /api/chat
                           ▼
                        FastAPI
                           │
                           ▼
                LangGraph Agentic RAG
                     Controller
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      Private HR Knowledge          Tavily Web Search
           Pinecone                 (Fallback Only)
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                         Groq
                    LLM Inference
                           │
                           ▼
                   Grounded Answer
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
        Citations                    Audit / Trace
                                      SQLite
```

 ### Core Design Principle

 The application follows a **private-first retrieval strategy**:

```
User Question
      ↓
Private HR Knowledge Base
      ↓
Is evidence sufficient?
   ┌──┴──┐
  YES    NO
   ↓      ↓
Answer   Tavily Web Search
          ↓
       Grade Evidence
          ↓
        Answer
```

 This reduces unnecessary external searches and helps keep company-specific answers grounded in internal policy.

---

 ## 4\. Agentic RAG Workflow

 The application uses **LangGraph** to orchestrate routing, retrieval, evidence grading, query rewriting, and answer generation.

```
Question
   ↓
[1] Route Question
   │
   ├── Greeting / Simple Chat
   │          ↓
   │     Direct Answer
   │
   └── HR / Policy Question
              ↓
[2] Retrieve from Private Pinecone KB
              ↓
[3] Grade Private Evidence
              │
        ┌─────┴─────┐
        │           │
      GOOD         WEAK
        │           │
        ▼           ▼
 Generate from   [4] Tavily Web Search
 Private KB              ↓
                   [5] Grade Web Evidence
                         │
                    ┌────┴────┐
                    │         │
                  GOOD       WEAK
                    │         │
                    ▼         ▼
              Generate Web   [6] Rewrite Query
              Answer             ↓
                           Retry Private KB
                                ↓
                         Max Retry Reached?
                                ↓
                       Insufficient Evidence
```

 ### Agent Responsibilities

 | Component | Responsibility |
| --- | --- |
| Router | Determines the type of user question |
| Private Retriever | Searches the internal HR knowledge base |
| Private Evidence Grader | Determines whether private evidence is relevant |
| Web Search | Retrieves current external information when required |
| Web Evidence Grader | Evaluates external search results |
| Query Rewriter | Improves weak or ambiguous queries |
| Answer Generator | Produces grounded responses |
| Audit Layer | Records workflow decisions and execution trace |

---

 ## 5\. Technology Stack

 | Layer | Technology | Purpose |
| --- | --- | --- |
| Agent Workflow | LangGraph | Stateful workflow, routing, and conditional decisions |
| LLM | Groq | Fast LLM inference for routing, grading, rewriting, and answer generation |
| LLM Model | `openai/gpt-oss-120b` | Primary language model |
| Embeddings | Hugging Face | Converts HR documents and queries into vector representations |
| Embedding Model | `Octen/Octen-Embedding-0.6B` | Generates document/query embeddings |
| Vector Database | Pinecone | Stores and retrieves private HR knowledge |
| External Search | Tavily | Fallback search for current public information |
| API | FastAPI | Backend REST API |
| Frontend | HTML/CSS/JavaScript | Employee-facing web interface |
| Audit | SQLite | Workflow and decision-path logging |
| Packaging | Docker | Reproducible application deployment |

---

 ## 6\. Models

 ### LLM

 The application uses **Groq** for LLM inference.

```
Provider: Groq
Model: openai/gpt-oss-120b
```

 The Groq model is used for tasks such as:

 - Question routing
- Evidence grading
- Query rewriting
- Answer generation
- Agent decision-making

 ### Embeddings

 The application uses a Hugging Face embedding model:

```
Model: Octen/Octen-Embedding-0.6B
```

 The embedding model converts both documents and user queries into numerical vectors.

```
HR Document
    ↓
Hugging Face Embedding Model
    ↓
Vector Representation
    ↓
Pinecone
```

 At query time:

```
User Question
    ↓
Hugging Face Embedding Model
    ↓
Query Vector
    ↓
Pinecone Similarity Search
    ↓
Relevant HR Documents
```

---

 ## 7\. Project Structure

```
Enterprise-HR-Policy-Agentic-RAG-Copilot/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── rag/
│   │   ├── state.py
│   │   ├── vectorstore.py
│   │   └── workflow.py
│   │
│   ├── services/
│   │   ├── audit.py
│   │   └── ingestion.py
│   │
│   └── main.py
│
├── data/
│   └── sample_kb/
│       ├── company_hr_handbook.md
│       └── hr_operations_runbook.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── uploads/
│
├── docs/
│   └── architecture.png
│
├── Dockerfile
├── ingest_sample_kb.py
├── requirements.txt
├── run.py
└── README.md
```

---

 ## 8\. Setup

 ### Step 1 — Clone the Repository

```
git clone <your-repository-url>
cd Enterprise-HR-Policy-Agentic-RAG-Copilot
```

 ### Step 2 — Create a Virtual Environment

```
python -m venv venv
```

 #### Windows

```
venv\Scripts\activate
```

 #### macOS/Linux

```
source venv/bin/activate
```

 ### Step 3 — Install Dependencies

```
pip install -r requirements.txt
```

---

 ## 9\. Environment Configuration

 Create a `.env` file based on `.env.example`.

 Example:

```
# Groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Hugging Face
HUGGINGFACE_EMBEDDINGS_MODEL=Octen/Octen-Embedding-0.6B

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=fde-hr-policy-rag
PINECONE_NAMESPACE=company-hr-kb

# Tavily
TAVILY_API_KEY=your_tavily_api_key_here

# Application
ADMIN_API_KEY=change-me-in-production
APP_ENV=development
```

 ### Environment Variables

 | Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | API key used for Groq LLM inference |
| `GROQ_MODEL` | Groq model used by the application |
| `HUGGINGFACE_EMBEDDINGS_MODEL` | Hugging Face embedding model |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `PINECONE_NAMESPACE` | Namespace containing company HR data |
| `TAVILY_API_KEY` | Tavily API key for external search |
| `ADMIN_API_KEY` | Key protecting HR document ingestion |
| `APP_ENV` | Application environment |

 > **Security:** Never commit `.env` or API keys to Git. Use environment variables or a production secret-management solution.

---

 ## 10\. Load Sample HR Knowledge

 After configuring Pinecone and the required API keys, ingest the sample HR documents:

```
python ingest_sample_kb.py
```

 The ingestion pipeline performs approximately:

```
HR Documents
      ↓
Document Loading
      ↓
Text Splitting / Chunking
      ↓
Hugging Face Embeddings
      ↓
Vector Generation
      ↓
Pinecone
      ↓
Private HR Knowledge Base
```

---

 ## 11\. Run the Application

 Start the application:

```
python run.py
```

 The application will be available at:

```
http://127.0.0.1:8080
```

 FastAPI Swagger documentation:

```
http://127.0.0.1:8080/docs
```

---

 ## 12\. Classroom Demo Scenarios

 ### Demo A — Private Knowledge Base Success

 Ask:

 > **How many annual leave days do employees receive?**

 Expected workflow:

```
Router
   ↓
Private KB Retrieval
   ↓
Private Evidence Grade → GOOD
   ↓
Generate from Private KB
```

 The answer should come from the internal HR handbook.

 No web search should be required.

---

 ### Demo B — Company Remote-Work Policy

 Ask:

 > **How many days per week can I work remotely?**

 Expected behavior:

```
Router
   ↓
Private KB Retrieval
   ↓
Evidence Grade → GOOD
   ↓
Generate from Private HR Policy
```

 The system should answer using the company's internal HR documentation.

---

 ### Demo C — Current External Information

 Ask:

 > **What are the latest public holiday rules in Bangladesh?**

 Expected workflow when the private KB does not contain sufficient information:

```
Router
   ↓
Private KB Retrieval
   ↓
Private Evidence Grade → WEAK
   ↓
Tavily Web Search
   ↓
Web Evidence Grade → GOOD
   ↓
Generate External Answer
```

 The response should make it clear that the information comes from external sources and may require HR validation.

---

 ### Demo D — Weak / Ambiguous Query

 Ask:

 > **What happens if mine is wrong?**

 The question is intentionally ambiguous.

 The workflow can:

```
Question
   ↓
Private KB Search
   ↓
Evidence → WEAK
   ↓
Web Search
   ↓
Evidence → WEAK
   ↓
Rewrite Query
   ↓
Retry Private KB
   ↓
Maximum Retry Reached
   ↓
Insufficient Evidence
```

 Instead of inventing an answer, the system should indicate that there is insufficient evidence.

---

 ## 13\. Document Ingestion

 Authorized HR users can add new company documents through the application.

 The ingestion flow is:

```
HR User
   ↓
Upload Document
   ↓
FastAPI /api/ingest
   ↓
Document Processing
   ↓
Chunking
   ↓
Hugging Face Embeddings
   ↓
Pinecone
   ↓
Updated HR Knowledge Base
```

 The ingestion endpoint is protected using an administrative API key.

 Example request header:

```
X-Admin-Key: <ADMIN_API_KEY>
```

---

 ## 14\. API Endpoints

 ### Chat

```
POST /api/chat
```

 Example request:

```
{
  "question": "How many annual leave days do employees receive?"
}
```

 Example response:

```
{
  "answer": "Employees receive ...",
  "source_used": "private_kb",
  "citations": [],
  "trace": [
    "Route question",
    "Retrieve private KB",
    "Grade private evidence",
    "Generate answer"
  ]
}
```

 ### Document Ingestion

```
POST /api/ingest
```

 Used by authorized HR users to upload new documents to the private knowledge base.

---

 ## 15\. Observability and Audit

 The application exposes the LangGraph execution path so developers and HR administrators can understand how an answer was produced.

 Example trace:

```
Route question
      ↓
Private KB retrieval
      ↓
Private evidence grading
      ↓
Evidence sufficient
      ↓
Generate grounded answer
```

 For a fallback scenario:

```
Route question
      ↓
Private KB retrieval
      ↓
Private evidence weak
      ↓
Tavily web search
      ↓
Web evidence grading
      ↓
Generate external answer
```

 The audit layer stores workflow information using SQLite.

 This helps with:

 - Debugging
- Agent observability
- Workflow analysis
- Evaluating retrieval quality
- Understanding fallback behavior
- Identifying failure cases

---

 ## 16\. Grounding Strategy

 The system is designed around a **retrieve → grade → generate** pattern.

 Instead of directly asking the LLM to answer:

```
Question
   ↓
LLM
   ↓
Answer
```

 the application uses:

```
Question
   ↓
Retrieve Evidence
   ↓
Grade Evidence
   ↓
Generate Grounded Answer
```

 This provides an additional control layer between the user's question and the final answer.

 ### Private Knowledge Priority

 The system prioritizes company-specific information:

```
Private HR KB
      ↓
Is evidence sufficient?
      │
      ├── YES → Use private evidence
      │
      └── NO → Search external sources
```

 This is important for HR applications because company policies should generally take precedence over generic internet information when answering company-specific questions.

---

 ## 17\. Security Considerations

 This project is designed as a demonstration/reference implementation and should be hardened before production deployment.

 Recommended production improvements include:

 - Authentication and authorization
- Role-based access control
- Employee identity integration
- Secure secret management
- API rate limiting
- Input validation
- File-type and file-size validation
- Malware scanning for uploaded documents
- PII detection and redaction
- Encryption at rest and in transit
- Detailed audit logging
- Document-level access control
- Tenant isolation
- Monitoring and alerting

 The `ADMIN_API_KEY` mechanism is intended for demonstration purposes and should be replaced with proper authentication and authorization in production.

---

 ## 18\. Docker

 Build the Docker image:

```
docker build -t enterprise-hr-rag .
```

 Run the container:

```
docker run --env-file .env -p 8080:8080 enterprise-hr-rag
```

 Then open:

```
http://127.0.0.1:8080
```

---

 ## 19\. End-to-End Data Flow

 ### Private HR Question

```
Employee
   ↓
Web UI
   ↓
FastAPI
   ↓
LangGraph
   ↓
Question Router
   ↓
Hugging Face Embedding Model
   ↓
Pinecone
   ↓
Relevant HR Documents
   ↓
Evidence Grader
   ↓
Groq
   ↓
Grounded Answer
   ↓
Employee
```

 ### External Information Question

```
Employee
   ↓
Web UI
   ↓
FastAPI
   ↓
LangGraph
   ↓
Private Pinecone Retrieval
   ↓
Evidence Weak
   ↓
Tavily
   ↓
Web Evidence Grading
   ↓
Groq
   ↓
External Answer + Source Information
   ↓
Employee
```

---

 ## 20\. What Changed From the IT Support Reference

 The overall application pattern remains based on the original IT Support Agentic RAG reference architecture.

 The following elements were adapted for the HR domain:

 - Business problem
- HR-specific prompts
- HR configuration names
- HR UI terminology
- Example questions
- Sample HR documents
- Knowledge-base content
- HR workflow descriptions
- HR document ingestion
- HR security considerations
- HR-focused documentation

 The core technical architecture remains centered around:

```
LangGraph
   +
Pinecone
   +
Groq
   +
Hugging Face Embeddings
   +
Tavily
   +
FastAPI
   +
HTML/CSS/JavaScript
   +
SQLite
   +
Docker
```

---

 ## 21. Key Learning Outcomes

 After completing this project, you should understand how to build an end-to-end Agentic RAG application rather than only an isolated RAG pipeline.

 You will learn:

 - How to design an Agentic RAG workflow with LangGraph
- How to build conditional agent routing
- How to integrate a private enterprise knowledge base
- How vector embeddings work with Pinecone
- How to use Hugging Face embedding models
- How to use Groq for LLM inference
- How to evaluate retrieved evidence
- How to implement web-search fallback
- How to rewrite and retry weak queries
- How to expose an agent through FastAPI
- How to build a simple employee-facing UI
- How to ingest new enterprise documents
- How to implement audit and workflow tracing
- How to package the application with Docker
- How to think about security and productionization

---

 ## 22\. End-to-End Architecture Summary

```
                         ┌──────────────────────┐
                         │    Employee / HR     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Web UI             │
                         │ HTML/CSS/JavaScript  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph       │
                         │  Agentic Controller  │
                         └──────────┬───────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
             ┌─────────────────┐        ┌─────────────────┐
             │ Hugging Face    │        │     Tavily      │
             │ Embeddings      │        │   Web Search    │
             └────────┬────────┘        └────────┬────────┘
                      │                           │
                      ▼                           │
             ┌─────────────────┐                  │
             │    Pinecone     │◄─────────────────┘
             │ Private HR KB   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Evidence Grader │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │      Groq       │
             │ GPT-OSS-120B    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Grounded Answer │
             └────────┬────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Employee UI        SQLite Audit
```

---

 ## 23\. Conclusion

 This project demonstrates how an Agentic RAG prototype can be transformed into a practical enterprise application.

 The key architectural principle is:

 > **Private knowledge first, evidence grading second, external search only when necessary, and grounded generation at the end.**

 By combining **LangGraph, Groq, Hugging Face Embeddings, Pinecone, Tavily, FastAPI, and a lightweight web interface**, the project provides a complete foundation for an enterprise HR Policy Copilot while demonstrating the broader responsibilities of a Forward Deployed Engineer.