# AI-Powered Customer Complaint Management System

An AI-powered Customer Complaint Management System designed for the pharmaceutical manufacturing industry.

The system helps capture, extract, assess, and manage customer complaints using Generative AI and a structured quality management workflow.

## Features

- Customer complaint intake
- AI-powered complaint information extraction
- Complaint processing from text/email
- PDF complaint text extraction
- AI-based risk assessment
- Severity classification
- Priority classification
- Risk score generation
- Suggested quality action
- AI assistant for natural-language complaint updates
- PostgreSQL complaint database
- Dynamic complaint dashboard
- Redux state management

## Technology Stack

### Frontend
- React
- Vite
- Redux Toolkit
- Axios
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

### AI
- Groq API
- OpenAI GPT-OSS 20B
- LangChain
- LangGraph

### Document Processing
- PyPDF

## System Architecture

```text
User
 |
 v
React Frontend
 |
 | HTTP / REST API
 v
FastAPI Backend
 |
 +------------------+
 |                  |
 v                  v
LangGraph          PostgreSQL
 |
 v
Groq LLM
 |
 v
Complaint Extraction
and Risk Assessment