import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { LocalIndex } from 'vectra'
import { z } from 'zod'
import path from 'path'
import { fileURLToPath } from 'url'
import { embed } from './embed.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const INDEX_PATH = path.join(__dirname, '..', '.index')

const index = new LocalIndex(INDEX_PATH)

const server = new McpServer({
  name: 'toip-knowledge-base',
  version: '0.1.0',
})

server.tool(
  'search',
  'Search ToIP meeting transcripts, summaries, and chats by semantic meaning',
  {
    query: z.string().describe('Natural language search query'),
    top_k: z.number().int().min(1).max(20).default(5).describe('Number of results to return'),
    filter_wg: z.string().optional().describe('Filter by working group (e.g. "Ecosystem Governance Working Group")'),
  },
  async ({ query, top_k, filter_wg }) => {
    if (!(await index.isIndexCreated())) {
      return {
        content: [{ type: 'text' as const, text: 'No index found. Run `npm run ingest` first.' }],
        isError: true,
      }
    }

    const vector = await embed(query)
    const results = await index.queryItems(vector, query, top_k * 3)

    const filtered = filter_wg
      ? results.filter((r) => {
          const units = JSON.parse((r.item.metadata.organizational_unit as string) ?? '[]') as string[]
          return units.some((u) => u.toLowerCase().includes(filter_wg.toLowerCase()))
        })
      : results

    const top = filtered.slice(0, top_k)

    if (top.length === 0) {
      return { content: [{ type: 'text' as const, text: 'No results found.' }] }
    }

    const output = top.map((r) => {
      const m = r.item.metadata
      const units = JSON.parse((m.organizational_unit as string) ?? '[]') as string[]
      return [
        `**${m.title}** (${m.date})`,
        `ID: ${m.doc_id} | ${m.content_type} | ${units.join(', ')}`,
        `Source: ${m.source_system}${m.source_url ? ` — ${m.source_url}` : ''}`,
        `Identifier: ${m.identifier}`,
        `Score: ${r.score.toFixed(3)}`,
        ``,
        m.chunk_text as string,
        `---`,
      ].join('\n')
    })

    return {
      content: [{ type: 'text' as const, text: output.join('\n') }],
    }
  }
)

server.tool(
  'list_documents',
  'List all documents in the knowledge base with their metadata',
  {},
  async () => {
    const all = await index.listItems()
    const seen = new Set<string>()
    const docs: string[] = []

    for (const item of all) {
      const id = item.metadata.doc_id as string
      if (seen.has(id)) continue
      seen.add(id)
      const m = item.metadata
      const units = JSON.parse((m.organizational_unit as string) ?? '[]') as string[]
      docs.push(`- **${m.title}** (${m.date}) [${m.content_type}] — ${units.join(', ')}`)
    }

    return {
      content: [{ type: 'text' as const, text: docs.join('\n') }],
    }
  }
)

const transport = new StdioServerTransport()
await server.connect(transport)
