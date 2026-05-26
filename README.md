# agentic-docs-rag-api

Agentic RAG API for document question-answering, powered by LangGraph, OpenAI, and Qdrant.

> **Status: Work in progress**

## Qdrant

Suba o Qdrant localmente com Docker:

```bash
docker compose up -d qdrant
```

Valide que o serviço está respondendo:

```bash
curl http://localhost:6333/healthz
```

Resposta esperada: `healthz check passed`
