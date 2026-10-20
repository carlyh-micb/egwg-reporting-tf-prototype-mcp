# MCP Data Generation

Tools for converting Zoom meeting exports into standardized JSON documents that can later be enriched with SAIDs, embeddings, vector search, and MCP retrieval.

## Overview

This project currently supports:

- Zoom closed caption files (`Recording.cc.vtt`)
- Zoom transcript files (`Recording.transcript.vtt`)
- Zoom chat files (`RecordingnewChat.txt`)

The conversion process normalizes each source file into a common JSON structure for later processing.

## Data Structure
- id - Unique identifier for this content item [we would want to standardize this].
- project - Trust over IP, etc.
- organizational_unit - Working group, task force, committee, etc. (list)
- date - Meeting date, publication date, or creation date.
- source_system - Zoom, GitHub, Confluence, YouTube, etc. (list)
- asset_type - Meeting, Video, Wiki Page, Issue, Specification, Report, etc. (list)
- content_type - Transcript, AI Summary, Chat, Markdown, Discussion, Description, etc. (list)
- title - Human-readable title.
- identifier - SAID, GitHub issue number, video ID, page ID, etc.
- identifier_type - SAID, GitHub Issue, YouTube Video, Confluence Page, etc. (list)
- source_url - Original source location.
- content - The text to be embedded and searched.
- collected_at - When the content was harvested.

## Folder Structure

```text
data/
├── raw/           # Original files from Zoom
├── processed/     # JSON files created by the parser
└── curated/       # JSON files after SAID generation
```

## Step 1: Add Raw Data

Copy Zoom exports into:

```text
data/raw/
```

Example:

```text
data/raw/
├── GMT20261001-145557_Recording.cc.vtt
├── GMT20261001-145557_Recording.transcript.vtt
└── GMT20261001-145557_RecordingnewChat.txt
```

## Step 2: Generate JSON Files

Run:

```bash
python vtt_to_json.py
```

This will:

- Read all files in `data/raw`
- Detect the content type
- Extract text
- Create JSON files in `data/processed`

Example output:

```text
data/processed/
├── GMT20261001-145557_Recording.cc.json
├── GMT20261001-145557_Recording.transcript.json
└── GMT20261001-145557_RecordingnewChat.json
```

## Step 3: Add Metadata

Open each generated JSON file and manually fill in missing metadata.

Example:

```json
{
  "project": "Trust over IP",

  "organizational_unit": [
    "Ecosystem Governance Working Group"
  ],

  "date": "2026-10-01",

  "title": "Ecosystem Governance Working Group Meeting",

  "source_url": "https://zoom.us/..."
}
```

### Required Fields

The following fields should be reviewed and completed:

```json
{
  "project": "",
  "organizational_unit": [],
  "date": "",
  "title": "",
  "source_url": ""
}
```

### Content Types

The parser automatically assigns:

| Source File | Content Type |
|-------------|-------------|
| `*.cc.vtt` | `ClosedCaptioning` |
| `*.transcript.vtt` | `Transcript` |
| `*.txt` | `Chat` |

## Step 4: Generate SAIDs

After metadata has been completed:

```bash
node scripts/saidify_all.js
```

This will:

- Read all JSON files from `data/processed`
- Generate a SAID
- Populate the `id` field
- Write the results to:

```text
data/curated/
```

Example:

```text
data/curated/
├── GMT20261001-145557_Recording.cc.json
├── GMT20261001-145557_Recording.transcript.json
└── GMT20261001-145557_RecordingnewChat.json
```

## Current Content Item Model

```json
{
  "id": "",

  "project": "",

  "organizational_unit": [],

  "date": "",

  "source_system": "Zoom",

  "asset_type": "Meeting",

  "content_type": "",

  "title": "",

  "identifier": "",
  "identifier_type": "SAID",

  "source_url": "",

  "content": "",

  "collected_at": ""
}
```

## Future Phases

Planned processing pipeline:

```text
Raw Files
    ↓
Processed JSON
    ↓
SAID Generation
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
MCP Server
    ↓
AI Client (Cursor)
```