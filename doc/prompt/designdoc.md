# Design Document Request — Learning Coach Agent (Hands-on Lab 1)

## Background

I am building the first hands-on project for my AI Systems Engineering course.

The objective is **not** to build a production-ready AI tutor.

Instead, this project serves as the first implementation of the concepts learned from **The Evolution of AI Agents**, including:

* Explicit Control Loop
* Explicit Learning State
* Separation of reasoning from workflow execution
* Stateful multi-turn interaction

This project is intentionally designed as an MVP and will be extended throughout later phases of the course.

---

# Project Goal

Design the architecture for a **Learning Coach Agent**.

The agent should continuously interact with a student, teach concepts, assess understanding, maintain learning state, and determine the next teaching step.

The emphasis is on **agent architecture**, not teaching quality.

---

# Scope (Lab 1)

The MVP should support only the minimum capabilities required to demonstrate an explicit learning agent.

The system should support:

* Teaching a concept
* Asking a follow-up question
* Assessing the student's response
* Updating learning state
* Deciding the next teaching step

The workflow should be deterministic and explicitly controlled by the backend.

The LLM should only perform reasoning tasks (e.g. teaching or assessment), and should not control the workflow itself.

---

# Out of Scope (Lab 1)

The following capabilities are intentionally excluded from this lab.

They are planned for later phases of the AI Systems Engineering roadmap.

* RAG
* Long-term Memory
* Planner
* Dynamic Workflow Generation
* Multi-Agent
* MCP
* LangGraph
* Complex Workflow Engines
* Production Deployment
* Authentication
* Database Optimization
* Advanced UI
* Cost Optimization

Please do **not** redesign the architecture to include these features at this stage.

---

# High-Level Architecture

The system should contain three primary components.

## Frontend

Responsibilities:

* Chat interface
* Display conversation
* Send user messages to backend
* Display assistant responses

A simple chat UI is sufficient.

---

## Backend

Responsibilities:

* Receive chat requests
* Load current learning state
* Execute the learning control loop
* Call the LLM when necessary
* Update learning state
* Return the next response

The backend owns the workflow.

---

## LLM

The LLM should only be responsible for reasoning tasks, such as:

* Teaching
* Explaining
* Assessing answers

The LLM should **not** determine workflow execution.

---

# Desired Control Loop

The MVP workflow should resemble the following.

Student Message

↓

Load Learning State

↓

Determine Current Mode

↓

If Teaching

* Generate explanation
* Ask a question
* Switch to Assess mode

↓

If Assessing

* Evaluate student's answer
* Update learning state

If understanding is sufficient

→ Move to the next topic

Otherwise

→ Reteach the current topic

↓

Save Learning State

↓

Return Response

---

# Learning State

Please propose a minimal but extensible learning state.

For example:

* student_id
* current_phase
* current_lesson
* current_topic
* current_mode
* last_question
* understanding_score
* misconceptions
* next_step

The state should be easy to extend later with:

* Memory
* RAG
* Planning
* Human-in-the-loop

without requiring major architectural changes.

---

# Backend Design

Please propose a backend architecture.

My current intuition is:

POST /chat

↓

Controller

↓

load_state()

↓

decide_next_step()

↓

teach()

or

assess()

↓

update_state()

↓

save_state()

↓

response

Please evaluate whether this architecture is appropriate.

If not, explain why and propose a better alternative.

---

# API Design

Please propose:

* REST endpoints
* Request / Response schema
* State update flow

The design should prioritize simplicity and future extensibility.

---

# Module Design

Please define the major backend modules and clearly describe the responsibility of each module.

For example:

* Controller
* State Manager
* Teaching Service
* Assessment Service
* State Store

Feel free to suggest a better decomposition if appropriate.

---

# Frontend

Keep the frontend intentionally simple.

A basic chat interface is sufficient.

The focus of this project is backend agent architecture.

---

# Future Extensibility

The architecture should make it straightforward to add later:

* Tool Calling
* Structured Output
* Memory
* RAG
* Planning
* Multi-step Workflow
* Human-in-the-loop
* Evaluation

The goal is to evolve the architecture incrementally rather than redesign it later.

---

# Design Trade-offs

For every major design decision, explain:

* Why this design was chosen
* Alternative designs
* Trade-offs
* Why the chosen design is appropriate for Lab 1

Avoid introducing unnecessary abstractions for future features.

---

# Deliverables

Please do **not** implement the project yet.

Instead, produce a complete Design Document including:

1. Overall architecture
2. Component responsibilities
3. Backend request flow
4. Learning state schema
5. API design
6. Module design
7. Suggested directory structure
8. Future extension strategy
9. Design trade-offs
10. Potential risks
11. Recommendations before implementation

The design should prioritize:

* Explicit control flow
* Simple architecture
* Clear module boundaries
* Future extensibility
* Incremental evolution throughout later labs
