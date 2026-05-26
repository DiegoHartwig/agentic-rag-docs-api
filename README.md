# Agentic Docs RAG API

API genérica de Agentic RAG para consulta de documentações técnicas, construída com FastAPI, Qdrant, embeddings locais e arquitetura modular.

---

## Objetivo

O projeto vai além de um chatbot simples com PDF. A proposta é uma API com ciclo completo de ingestão e consulta de documentação técnica:

- Gestão de collections no banco vetorial
- Upload de documentos (PDF, TXT, Markdown)
- Extração de texto e chunking
- Geração de embeddings locais
- Indexação no Qdrant
- Recuperação via RAG (próximas etapas)
- Agente com uso controlado de ferramentas (próximas etapas)

O objetivo final é um agente capaz de decidir, de forma autônoma, quando buscar no contexto dos documentos, quando responder diretamente, quando calcular e quando acionar outras ferramentas — sem depender de chamadas fixas.

---

## Status do projeto

> **Em desenvolvimento — MVP em construção**

### Implementado

- [x] Estrutura inicial do projeto
- [x] FastAPI com endpoint `/health`
- [x] Docker Compose com Qdrant
- [x] Endpoints de collections (`POST`, `GET`, `DELETE`)
- [x] Loaders para PDF, TXT e Markdown
- [x] Chunking de documentos
- [x] Embeddings locais com FastEmbed
- [x] Upload e indexação de documentos no Qdrant

### Próximos passos

- [ ] Listagem de documentos indexados
- [ ] Remoção de documentos por `document_id`
- [ ] Retrieval tool
- [ ] Calculator tool
- [ ] Agente com LangGraph
- [ ] Endpoint `/chat`
- [ ] README final com exemplos completos
- [ ] Post técnico para LinkedIn

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI |
| Banco vetorial | Qdrant |
| Embeddings | FastEmbed |
| Extração de PDF | PyMuPDF |
| Orquestração de agentes | LangGraph / LangChain |
| Validação e configuração | Pydantic / Pydantic Settings |
| Infraestrutura local | Docker Compose |
| Linting | Ruff |
| Testes | Pytest |
| Linguagem | Python 3.11+ |

---

## Execução local

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose

### Configuração

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Copie o arquivo de exemplo e ajuste as variáveis conforme necessário:

```bash
cp .env.example .env
```

### Subir o Qdrant

```bash
docker compose up -d qdrant
```

Validar que o serviço está respondendo:

```bash
curl http://localhost:6333/healthz
```

### Rodar a API

```bash
uvicorn app.main:app --reload
```

### Documentação interativa

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Qdrant Dashboard: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## Exemplo de fluxo atual

Com o Qdrant e a API rodando, o fluxo básico é:

1. **Criar uma collection** via `POST /collections` informando o nome (ex: `trino`, `dbt`, `spark`).
2. **Fazer upload de um documento** via `POST /documents/upload`, informando o arquivo (PDF, TXT ou Markdown) e a collection de destino.
3. **Verificar a indexação** no Qdrant Dashboard ou via `GET /collections`.

A cada upload, o documento é extraído, dividido em chunks, vetorizado localmente e salvo no Qdrant com metadados (nome do arquivo, página, índice do chunk, tags e tipo de fonte).

---

## Limitações do MVP

- PDFs escaneados (imagens) não possuem suporte a OCR; o texto extraído pode ser vazio ou incompleto.
- O agente conversacional ainda não foi implementado.
- A busca via RAG será implementada nas próximas etapas.
- O suporte a OpenAI é opcional; o MVP utiliza embeddings locais (FastEmbed) para permitir execução sem custo em ambiente de demonstração.
