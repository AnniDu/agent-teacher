# AI Systems Engineering

## Part 1 — Foundations & Evolution

### Course Goal

Learn to design, build, deploy, and evolve production-grade AI systems from first principles.

---

# Phase 0 — LLM Foundations

**Goal:** Build the mathematical intuition and architectural understanding behind modern LLMs.

### Lesson 0.1 — Representation Learning Foundations

**Goal:** Understand why AI represents knowledge as vectors and how vector operations capture semantic relationships.

**Topics**

* Scalar, Vector, Matrix, Tensor
* Vector Space Intuition
* Dot Product
* Cosine Similarity
* Distance & Projection
* Linear Combination
* Why AI Represents Knowledge as Vectors

---

### Lesson 0.2 — Embedding

**Goal:** Understand how discrete tokens are transformed into continuous semantic representations.

**Topics**

* Tokenization
* Vocabulary
* Embedding
* Semantic Space
* Similarity Search

---

### Lesson 0.3 — Attention

**Goal:** Understand how tokens selectively exchange information through attention mechanisms.

**Topics**

* Self-Attention
* Query / Key / Value
* Attention Score
* Softmax
* Weighted Sum

---

### Lesson 0.4 — Transformer Block

**Goal:** Understand how the major components of a Transformer layer work together to process information.

**Topics**

* Multi-Head Attention
* Feed Forward Network (FFN)
* Residual Connection
* LayerNorm
* Position Encoding

---

### Lesson 0.5 — Complete Transformer

**Goal:** Understand the complete forward pass and information flow of a Transformer model.

**Topics**

* Complete Forward Pass
* Information Flow
* Why Transformer Works

---

# Phase 1 — The Evolution of AI Agents

**Goal:** Understand why modern AI agents evolved into their current architecture.

### Lesson 1.1 — Prompt Engineering

**Goal:** Understand how prompts guide LLM behavior and why prompting alone is insufficient for building reliable AI systems.

**Topics**

* Prompt Engineering
* In-Context Learning
* Few-shot Learning

---

### Lesson 1.2 — Chain of Thought

**Goal:** Understand how explicit reasoning improves LLM performance and where pure reasoning reaches its limits.

**Topics**

* Chain of Thought
* Intermediate Reasoning
* Self-Consistency
* Why Reasoning Changed LLMs
* Limitations of Pure Reasoning

---

### Lesson 1.3 — ReAct

**Goal:** Understand how reasoning and action are combined to enable interaction with external tools and environments.

**Topics**

* Thought
* Action
* Observation
* Tool Interaction
* Closed Feedback Loop

---

### Lesson 1.4 — Reflection

**Goal:** Understand how agents improve their behavior through self-evaluation and feedback.

**Topics**

* Reflection
* Feedback
* Verbal Memory
* Learning from Mistakes

---

### Lesson 1.5 — AutoGPT

**Goal:** Understand the strengths, limitations, and engineering lessons of fully autonomous LLM agents.

**Topics**

* Goal-driven Execution
* Continuous Autonomy
* LLM-centric Control
* Infinite Loops
* Goal Drift
* Cost Explosion
* Engineering Lessons

---

### Lesson 1.6 — BabyAGI

**Goal:** Understand how task decomposition and task management improve long-running autonomous execution.

**Topics**

* Task Decomposition
* Task Queue
* Task Generation
* Task Prioritization
* Long-running Planning

---

### Lesson 1.7 — Workflow Engineering

**Goal:** Understand why modern AI systems separate reasoning from deterministic workflow execution.

**Topics**

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

---

### Hands-on Lab 1 — Build a Learning Coach Agent

**Goal:** Apply the concepts from Phase 1 by building the first version of a stateful Learning Coach Agent.

**Topics**

* Learning State
* Teaching Workflow
* Drift Detection
* Dry Note Generation
* Progress Tracking

# Phase 2 — Agent Building Blocks

**Goal:** Build every core capability required to develop modern AI agents.

---

### Lesson 2.1 — Tool Calling

**Goal:** Understand how AI agents interact with external systems by separating reasoning from execution.

**Topics**

* Function Calling
* Tool Calling
* Tool Schema
* Tool Selection
* Tool Execution
* Tool Result Handling

---

### Lesson 2.2 — Structured Output

**Goal:** Learn how to produce reliable, machine-readable outputs that can be safely consumed by downstream systems.

**Topics**

* JSON Output
* Schema Validation
* Pydantic
* Output Parsing
* Error Recovery

---

### Lesson 2.3 — Memory

**Goal:** Understand how AI agents store, retrieve, and manage information across interactions.

**Topics**

* Working Memory
* Episodic Memory
* Semantic Memory
* Long-term Memory
* Memory Retrieval
* When NOT to Use Memory

---

### Lesson 2.4 — Knowledge Systems (RAG)

**Goal:** Understand how retrieval augments reasoning by separating knowledge storage from language models.

**Topics**

* Document Loading
* Chunking
* Embedding
* Vector Search
* Retrieval Pipeline
* RAG Failure Modes

---

### Lesson 2.5 — Multi-step Workflow

**Goal:** Learn how complex agent behavior emerges by coordinating multiple reasoning and execution steps.

**Topics**

* Planner
* Executor
* Re-planning
* State Passing
* Control Flow

---

### Lesson 2.6 — Human-in-the-loop

**Goal:** Understand how human supervision improves the reliability, safety, and controllability of AI systems.

**Topics**

* Approval
* Review
* Interrupt
* Resume
* Permission Boundaries

---

### Lesson 2.7 — Evaluation

**Goal:** Learn how to systematically measure, compare, and improve AI agent performance.

**Topics**

* Agent Evaluation
* Tool Evaluation
* RAG Evaluation
* LLM-as-a-Judge
* Regression Testing

---

### Lesson 2.8 — Agent Design Patterns

**Goal:** Understand common architectural patterns that can be reused to build scalable AI agents.

**Topics**

* Router
* Planner
* Executor
* Critic
* Reviewer
* Manager
* Worker
* Supervisor

---

### Hands-on Lab 2 — Upgrade the Learning Coach Agent

**Goal:** Apply the concepts from Phase 2 by extending the Learning Coach Agent with modern agent capabilities.

**Topics**

* Tool Calling
* Memory
* RAG
* Planning
* Human-in-the-loop
* Evaluation

---

# Phase 3 — Agent Runtime Architecture

**Goal:** Learn how reliable AI agents are engineered to execute in production environments.

---

### Lesson 3.1 — Workflow Graph

**Goal:** Understand how agent execution can be modeled as composable workflow graphs.

**Topics**

* Graph
* Node
* Edge
* Conditional Routing
* Loop
* Subgraph

---

### Lesson 3.2 — State Management

**Goal:** Learn how to design explicit, maintainable, and reliable state for AI systems.

**Topics**

* Shared State
* State Schema
* State Isolation
* State Versioning

---

### Lesson 3.3 — Runtime

**Goal:** Understand how runtime systems enable durable, fault-tolerant agent execution.

**Topics**

* Runtime
* Checkpoint
* Resume
* Retry
* Timeout
* Durable Execution

---

### Lesson 3.4 — Event-driven Architecture

**Goal:** Understand how asynchronous and event-driven execution improves scalability and responsiveness.

**Topics**

* Streaming
* Event Bus
* Async Execution
* Background Jobs
* Cancellation

---

### Lesson 3.5 — Versioning

**Goal:** Learn how to safely evolve AI systems while maintaining compatibility and reproducibility.

**Topics**

* Prompt Versioning
* Workflow Versioning
* State Migration
* Artifact Versioning

---

### Lesson 3.6 — Observability

**Goal:** Learn how to inspect, monitor, debug, and optimize AI systems running in production.

**Topics**

* Logging
* Tracing
* Run ID
* Metrics
* Token Tracking
* Latency
* Cost Tracking

---

### Lesson 3.7 — Framework Case Studies *(Optional)*

**Goal:** Compare how different AI frameworks implement the same architectural concepts and engineering principles.

**Topics**

* LangGraph
* PocketFlow
* PydanticAI
* OpenAI Agents SDK
* MCP
* Google ADK
* Claude Code
* Codex
* OpenHands

---

### Hands-on Lab 3 — Build a Framework-based Agent

**Goal:** Apply the concepts from Phase 3 by implementing an AI agent using a modern agent framework.

**Topics**

* Framework Migration
* MCP Integration
* Multi-Agent Collaboration

# Phase 4 — Production AI Systems

**Goal:** Learn how to deploy, operate, monitor, and continuously improve AI systems in production.

---

### Lesson 4.1 — Deployment

**Goal:** Learn how to package and deploy AI systems as reliable production services.

**Topics**

* FastAPI
* Docker
* Docker Compose
* Environment Variables
* Secrets Management

---

### Lesson 4.2 — Monitoring

**Goal:** Understand how to observe the health, reliability, and performance of production AI systems.

**Topics**

* Logging
* Metrics
* Tracing
* Alerting
* Error Tracking

---

### Lesson 4.3 — Production Evaluation

**Goal:** Learn how to continuously evaluate deployed AI systems using both automated metrics and human feedback.

**Topics**

* Offline Evaluation
* Online Evaluation
* Human Feedback
* A/B Testing

---

### Lesson 4.4 — Cost Management

**Goal:** Understand how to balance model quality, latency, and operational cost in production environments.

**Topics**

* Token Cost
* Tool Cost
* Prompt Cache
* Model Routing
* Budget Control

---

### Lesson 4.5 — Safety & Guardrails

**Goal:** Learn how to build AI systems that operate safely, predictably, and within defined boundaries.

**Topics**

* Prompt Versioning
* Guardrails
* Safety Policies
* Permission Control

---

### Lesson 4.6 — Scaling & Serving *(Optional)*

**Goal:** Understand the infrastructure and optimization techniques behind large-scale LLM serving.

**Topics**

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

---

### Hands-on Lab 4 — Deploy the Learning Coach Agent

**Goal:** Apply the concepts from Phase 4 by deploying, monitoring, evaluating, and optimizing the Learning Coach Agent in a production-like environment.

**Topics**

* Production Deployment
* Monitoring
* Evaluation
* Cost Optimization
* Scaling

---

# Phase 5 — AI System Design

**Goal:** Learn how to design complete AI systems by making sound engineering decisions under real-world constraints.

---

### Lesson 5.1 — Requirement Analysis

**Goal:** Learn how to translate user needs and business requirements into clear system requirements.

**Topics**

* Requirement Analysis
* User Goals
* System Constraints
* Failure Modes

---

### Lesson 5.2 — Architecture Design

**Goal:** Learn how to design the overall architecture of an AI system by identifying components, responsibilities, and system boundaries.

**Topics**

* Component Design
* Agent Architecture
* System Diagram
* Boundary Definition

---

### Lesson 5.3 — Architecture Trade-offs

**Goal:** Learn how to evaluate architectural decisions by balancing cost, quality, latency, flexibility, scalability, and maintainability.

**Topics**

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

---

### Lesson 5.4 — Workflow Design

**Goal:** Learn how to design reliable workflows that coordinate reasoning, tools, state, and human interaction.

**Topics**

* Control Flow
* State Flow
* Tool Flow
* Approval Flow

---

### Lesson 5.5 — Runtime Design

**Goal:** Learn how to design runtime strategies that ensure reliable long-running execution and failure recovery.

**Topics**

* Failure Recovery
* Checkpoint Strategy
* Retry Strategy
* Long-running Execution

---

### Lesson 5.6 — Production Deployment

**Goal:** Learn how to deploy a complete AI system using production engineering best practices.

**Topics**

* API Service
* Database
* CI/CD
* Monitoring
* Scaling

---

### Lesson 5.7 — Continuous Improvement

**Goal:** Learn how to continuously improve AI systems through evaluation, regression testing, performance optimization, and operational feedback.

**Topics**

* Evaluation
* Regression Testing
* Failure Analysis
* Cost Optimization
* Performance Optimization

---

### Final Project — Build a Production AI System

**Goal:** Apply the knowledge from the entire course by designing, building, deploying, evaluating, and iteratively improving a complete production-grade AI system.

**Topics**

* Design Your Own Architecture
* Design Your Own Workflow
* Design Your Own State
* Design Your Own Runtime
* Deploy to Production
* Evaluate Performance
* Optimize Cost
* Scale the System

