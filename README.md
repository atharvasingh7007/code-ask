# CodeAsk — AI Agent for Codebase Q&A

**Track 1 Project: Build and Deploy an ADK Agent on Cloud Run**

A single ADK agent that answers questions about a provided codebase. Ask anything about the code — it reads, understands, and explains.

## What It Does

- Takes a code snippet or repository description as input
- Answers questions about code structure, logic, and purpose
- Uses Gemini 2.0 Flash for inference
- HTTP POST endpoint → JSON response
- Persistent session memory via ContextBridge sidecar

## Architecture

```
User → CodeAsk Agent (Cloud Run) → Gemini API
                         ↓
                   ContextBridge (persistent memory)
```

## API

**POST /agent**

```json
{
  "session_id": "uuid",
  "code": "def hello(): print('world')",
  "question": "What does this function do?"
}
```

**Response:**
```json
{
  "answer": "This function prints 'world' to stdout.",
  "session_id": "uuid",
  "tokens_used": 120
}
```

## Deploy

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/genai-academy-apac-2/code-ask/code-ask:latest
gcloud run deploy code-ask \
  --image=us-central1-docker.pkg.dev/genai-academy-apac-2/code-ask/code-ask:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```
