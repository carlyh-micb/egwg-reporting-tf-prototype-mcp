# ToIP MCP Server

Local MCP server for semantic search over ToIP meeting transcripts, closed captions, and chat logs. No API key required — embeddings run locally via `@xenova/transformers`.

## Setup

```bash
npm install
```

## Ingest

Fetches all documents from the data repo, chunks them, embeds with a local model, and writes a local vector index (~25 MB model downloaded on first run):

```bash
npm run ingest
```

## Run

```bash
npm start
```

## Cursor / Claude Desktop config

Add to your MCP config:

```json
{
  "mcpServers": {
    "toip-knowledge-base": {
      "command": "node",
      "args": ["/absolute/path/to/toip-mcp-server/dist/index.js"]
    }
  }
}
```

Or for development (no build step):

```json
{
  "mcpServers": {
    "toip-knowledge-base": {
      "command": "npx",
      "args": ["tsx", "/absolute/path/to/toip-mcp-server/src/index.ts"]
    }
  }
}
```

## Tools

- **search** — semantic search over all document chunks. Returns matching passages with title, date, WG, source, and identifier. Supports optional `filter_wg` to narrow by working group.
- **list_documents** — list all indexed documents with metadata.

## Data schema

Each document follows the schema at [carlyh-micb/mcp_data_generation](https://github.com/carlyh-micb/mcp_data_generation):

| Field | Description |
|---|---|
| `id` | Stable human-readable identifier |
| `project` | e.g. "Trust over IP" |
| `organizational_unit` | WG/TF array |
| `date` | Meeting or publication date |
| `source_system` | Zoom, GitHub, Confluence, YouTube... |
| `content_type` | Transcript, ClosedCaptioning, Chat... |
| `identifier` | SAID (`urn:said:...`) |
| `content` | Full text (chunked for search) |
