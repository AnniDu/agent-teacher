# AI Systems Engineering

## Part 1 — Foundations & Evolution

### Course Goal

Learn to design, build, deploy, and evolve production-grade AI systems from first principles.

---

# Phase 0 — LLM Foundations

**Goal:** Build the mathematical intuition and architectural understanding behind modern LLMs.

### Lesson 0.1 — Representation Learning Foundations

**Goal:** Understand why AI represents knowledge as vectors.

Topics

* Scalar, Vector, Matrix, Tensor
* Vector Space Intuition
* Dot Product
* Cosine Similarity
* Distance & Projection
* Linear Combination
* Why AI Represents Knowledge as Vectors

### Lesson 0.2 — Embedding

**Goal:** Understand how discrete tokens become continuous vector representations.

Topics

* Tokenization
* Vocabulary
* Embedding
* Semantic Space
* Similarity Search

### Lesson 0.3 — Attention

**Goal:** Understand how tokens exchange information through attention.

Topics

* Self-Attention
* Query / Key / Value
* Attention Score
* Softmax
* Weighted Sum

### Lesson 0.4 — Transformer Block

**Goal:** Understand how a Transformer layer processes information.

Topics

* Multi-Head Attention
* Feed Forward Network (FFN)
* Residual Connection
* LayerNorm
* Position Encoding

### Lesson 0.5 — Complete Transformer

**Goal:** Understand the complete forward pass and information flow of a Transformer.

Topics

* Complete Forward Pass
* Information Flow
* Why Transformer Works

---

# Phase 1 — The Evolution of AI Agents

**Goal:** Understand why modern AI agents evolved into their current architecture.

### Lesson 1.1 — Prompt Engineering

Topics

* Prompt Engineering
* In-Context Learning
* Few-shot Learning

### Lesson 1.2 — Chain of Thought

Topics

* Chain of Thought
* Intermediate Reasoning
* Self-Consistency
* Why Reasoning Changed LLMs
* Limitations of Pure Reasoning

### Lesson 1.3 — ReAct

Topics

* Thought
* Action
* Observation
* Tool Interaction
* Closed Feedback Loop

### Lesson 1.4 — Reflection

Topics

* Reflection
* Feedback
* Verbal Memory
* Learning from Mistakes

### Lesson 1.5 — AutoGPT

Topics

* Goal-driven Execution
* Continuous Autonomy
* LLM-centric Control
* Infinite Loops
* Goal Drift
* Cost Explosion
* Engineering Lessons

### Lesson 1.6 — BabyAGI

Topics

* Task Decomposition
* Task Queue
* Task Generation
* Task Prioritization
* Long-running Planning

### Lesson 1.7 — Workflow Engineering

Topics

* Explicit Control Loop
* Deterministic Control Flow
* Separating Reasoning from Execution
* Shared State
* Runtime
* Checkpoint
* Retry
* Resume
* Time Travel
* Human-in-the-loop
* Observability

### Hands-on Lab 1 — Build a Learning Coach Agent

Topics

* Learning State
* Teaching Workflow
* Drift Detection
* Dry Note Generation
* Progress Tracking

# AI Systems Engineering

## Part 2 — Building & Engineering Agents

# Phase 2 — Agent Building Blocks

**Goal:** Build every core capability of a modern AI agent.

### Lesson 2.1 — Tool Calling

Topics

* Function Calling
* Tool Calling
* Tool Schema
* Tool Selection
* Tool Execution
* Tool Result Handling

### Lesson 2.2 — Structured Output

Topics

* JSON Output
* Schema Validation
* Pydantic
* Output Parsing
* Error Recovery

### Lesson 2.3 — Memory

Topics

* Working Memory
* Episodic Memory
* Semantic Memory
* Long-term Memory
* Memory Retrieval
* When NOT to Use Memory

### Lesson 2.4 — Knowledge Systems (RAG)

Topics

* Document Loading
* Chunking
* Embedding
* Vector Search
* Retrieval Pipeline
* RAG Failure Modes

### Lesson 2.5 — Multi-step Workflow

Topics

* Planner
* Executor
* Re-planning
* State Passing
* Control Flow

### Lesson 2.6 — Human-in-the-loop

Topics

* Approval
* Review
* Interrupt
* Resume
* Permission Boundaries

### Lesson 2.7 — Evaluation

Topics

* Agent Evaluation
* Tool Evaluation
* RAG Evaluation
* LLM-as-a-Judge
* Regression Testing

### Lesson 2.8 — Agent Design Patterns

Topics

* Router
* Planner
* Executor
* Critic
* Reviewer
* Manager
* Worker
* Supervisor

### Hands-on Lab 2 — Upgrade the Learning Coach Agent

Topics

* Tool Calling
* Memory
* RAG
* Planning
* Human-in-the-loop
* Evaluation

---

# Phase 3 — Agent Runtime Architecture

**Goal:** Learn how reliable AI agents execute in production.

### Lesson 3.1 — Workflow Graph

Topics

* Graph
* Node
* Edge
* Conditional Routing
* Loop
* Subgraph

### Lesson 3.2 — State Management

Topics

* Shared State
* State Schema
* State Isolation
* State Versioning

### Lesson 3.3 — Runtime

Topics

* Runtime
* Checkpoint
* Resume
* Retry
* Timeout
* Durable Execution

### Lesson 3.4 — Event-driven Architecture

Topics

* Streaming
* Event Bus
* Async Execution
* Background Jobs
* Cancellation

### Lesson 3.5 — Versioning

Topics

* Prompt Versioning
* Workflow Versioning
* State Migration
* Artifact Versioning

### Lesson 3.6 — Observability

Topics

* Logging
* Tracing
* Run ID
* Metrics
* Token Tracking
* Latency
* Cost Tracking

### Lesson 3.7 — Framework Case Studies *(Optional)*

Topics

* LangGraph
* PocketFlow
* PydanticAI
* OpenAI Agents SDK
* MCP
* Google ADK
* Claude Code
* Codex
* OpenHands

### Hands-on Lab 3 — Build a Framework-based Agent

Topics

* Framework Migration
* MCP Integration
* Multi-Agent Collaboration

# AI Systems Engineering

## Part 3 — Production & System Design

# Phase 4 — Production AI Systems

**Goal:** Deploy, monitor, evaluate, and operate AI systems in production.

### Lesson 4.1 — Deployment

Topics

* FastAPI
* Docker
* Docker Compose
* Environment Variables
* Secrets Management

### Lesson 4.2 — Monitoring

Topics

* Logging
* Metrics
* Tracing
* Alerting
* Error Tracking

### Lesson 4.3 — Production Evaluation

Topics

* Offline Evaluation
* Online Evaluation
* Human Feedback
* A/B Testing

### Lesson 4.4 — Cost Management

Topics

* Token Cost
* Tool Cost
* Prompt Cache
* Model Routing
* Budget Control

### Lesson 4.5 — Safety & Guardrails

Topics

* Prompt Versioning
* Guardrails
* Safety Policies
* Permission Control

### Lesson 4.6 — Scaling & Serving *(Optional)*

Topics

* vLLM
* SGLang
* TensorRT-LLM
* Continuous Batching
* KV Cache
* Paged Attention
* FlashAttention
* GPU Utilization
* Load Balancing
* Autoscaling

### Hands-on Lab 4 — Deploy the Learning Coach Agent

Topics

* Production Deployment
* Monitoring
* Evaluation
* Cost Optimization
* Scaling

---

# Phase 5 — AI System Design

**Goal:** Design, implement, deploy, and continuously improve a complete production-grade AI system.

### Lesson 5.1 — Requirement Analysis

Topics

* Requirement Analysis
* User Goals
* System Constraints
* Failure Modes

### Lesson 5.2 — Architecture Design

Topics

* Component Design
* Agent Architecture
* System Diagram
* Boundary Definition

### Lesson 5.3 — Architecture Trade-offs

Topics

* Simplicity vs Flexibility
* Latency vs Quality
* Cost vs Performance
* Deterministic Workflow vs Agentic Workflow
* Small Model vs Large Model
* RAG vs Fine-tuning
* Memory vs Retrieval
* Single Agent vs Multi-Agent
* Sync vs Async
* Self-hosted vs API Models
* Human-in-the-loop vs Full Automation
* Build vs Buy

### Lesson 5.4 — Workflow Design

Topics

* Control Flow
* State Flow
* Tool Flow
* Approval Flow

### Lesson 5.5 — Runtime Design

Topics

* Failure Recovery
* Checkpoint Strategy
* Retry Strategy
* Long-running Execution

### Lesson 5.6 — Production Deployment

Topics

* API Service
* Database
* CI/CD
* Monitoring
* Scaling

### Lesson 5.7 — Continuous Improvement

Topics

* Evaluation
* Regression Testing
* Failure Analysis
* Cost Optimization
* Performance Optimization

### Final Project — Build a Production AI System

Topics

* Design Your Own Architecture
* Design Your Own Workflow
* Design Your Own State
* Design Your Own Runtime
* Deploy to Production
* Evaluate Performance
* Optimize Cost
* Scale the System

