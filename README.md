# MCP Knowledge Retrieval Platform

## Overview

This project provides a framework for collecting, normalizing, indexing, and retrieving organizational knowledge from multiple source systems.

Content is collected in its original format, transformed into a common document model, assigned a SAID, indexed for semantic search, and exposed through an MCP server.

Supported and planned sources include:

- Zoom
- Confluence
- GitHub
- YouTube

---

## Architecture

```text
Source Systems
    ↓
Raw Content
    ↓
Ingestion Engine
    ↓
Source Parser
    ↓
Document Model
    ↓
SAID Generation
    ↓
Processed Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Index
    ↓
MCP Server
```

---

## Repository Structure

```text
data/
├── raw/
├── processed/
└── ingestion_registry.json
```

### Raw Content

Raw content is retained in its original format and serves as the system of record.

Examples:

```text
.vtt
.txt
.md
.html
.pdf
.json
```

Example:

```text
data/raw/zoom/egwg/
├── metadata.json
├── GMT20261001-145557_Recording.transcript.vtt
├── GMT20261001-145557_Recording.cc.vtt
└── GMT20261001-145557_RecordingnewChat.txt
```

### Organizational Metadata

Each organizational unit may contain a `metadata.json` file.

Example:

```json
{
  "project": "Trust over IP",
  "organizational_unit": [
    "Ecosystem Governance Working Group"
  ],
  "title": "Ecosystem Governance Working Group Meeting",
  "source_url":""
}
```

This metadata is inherited by content within the folder hierarchy.

---

## Ingestion Engine

The ingestion engine:

- Walks the `data/raw` directory tree
- Detects source systems
- Dispatches files to source-specific parsers
- Maintains an ingestion registry
- Generates SAIDs
- Saves processed documents

Current parser:

- Zoom

Future parsers:

- Confluence
- GitHub
- YouTube

---

## Ingestion Registry

The ingestion registry prevents reprocessing unchanged files.

Example:

```json
{
  "data/raw/zoom/egwg/file.vtt": {
    "file_hash": "...",
    "processed_at": "..."
  }
}
```

Processing logic:

```text
File discovered
    ↓
Calculate SHA-256
    ↓
Compare with registry
    ↓
Unchanged → Skip
Changed → Process
```

---

## Document Model

All content is normalized into a common structure before indexing.

```json
{
  "identifier": "",

  "project": "",
  "organizational_unit": [],

  "source_system": "",
  "source_identifier": "",
  "source_url": "",

  "date": "",

  "asset_type": "",
  "content_type": "",
  "title": "",

  "content": ""
}
```

### Fields

| Field | Description |
|---------|-------------|
| identifier | SAID assigned to the normalized document |
| project | Associated project or initiative |
| organizational_unit | Associated organizational groups |
| source_system | Origin system |
| source_identifier | Native identifier from the source system |
| source_url | URL where the content originated |
| date | Date associated with the content |
| asset_type | High-level asset type |
| content_type | Type of extracted content |
| title | Human-readable title |
| content | Text used for indexing and retrieval |

---

## Processing Pipeline

```text
Raw File
    ↓
Source Parser
    ↓
Document Model
    ↓
SAID Generation
    ↓
Processed JSON Document
```

Processed documents are the input for:

```text
Chunking
    ↓
Embeddings
    ↓
Vector Search
```

---

## Components

### mcp_data_generation

Responsible for:

- Content discovery
- Metadata loading
- Parsing source content
- Document normalization
- SAID generation

Output:

```text
Processed JSON Documents
```

### mcp_embeddings

Responsible for:

- Chunking
- Embedding generation
- Vector index creation

### toip-mcp-server

Provides retrieval capabilities through MCP.

Current tools:

```text
search()
list_documents()
```

### mcp_testing

Client used for testing and validating MCP retrieval behavior.

---

## Objectives

- Support multiple content sources.
- Preserve original source artifacts.
- Normalize content into a common model.
- Generate persistent document identifiers.
- Enable semantic search and retrieval.
- Expose knowledge through MCP.