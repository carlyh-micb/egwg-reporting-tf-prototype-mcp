# ToIP MCP Server

Local MCP server for semantic search over ToIP meeting transcripts, closed captions, and chat logs. No API key required — embeddings run locally via `fastembed`.

## Setup

```bash
npm install
```

## Ingest

Fetches all documents from the data repo, chunks them, embeds with a local model, and writes a local vector index (~25 MB model downloaded on first run):

```bash
npm run ingest
```

## Query the index directly

Prints the raw JSON of the top matching chunks (5 by default, up to 20), without going through the MCP server:

```bash
npm run query "bite size trust scripts"
npm run query -- --limit 10 "bite size trust scripts"
```

The results are unfiltered, straight from the index. They can differ from the MCP `search` tool when `filter_wg` is used, because the tool filters by working group after querying. Scores are the same for the same query, since both use the same embedding and index.

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
