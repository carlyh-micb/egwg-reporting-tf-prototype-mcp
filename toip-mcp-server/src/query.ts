import { LocalIndex } from 'vectra'
import path from 'path'
import { fileURLToPath } from 'url'
import { embed } from './embed.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const index = new LocalIndex(path.join(__dirname, '..', '.index'))

const usage = 'Usage: npm run query -- [--limit N] "your question"'
const args = process.argv.slice(2)
let limit = 5
const limitAt = args.indexOf('--limit')
if (limitAt !== -1) {
  limit = Number(args[limitAt + 1])
  args.splice(limitAt, 2)
  if (!Number.isInteger(limit) || limit < 1 || limit > 20) {
    console.error('--limit must be an integer between 1 and 20')
    console.error(usage)
    process.exit(1)
  }
}

const query = args.join(' ')
if (!query) {
  console.error(usage)
  process.exit(1)
}

if (!(await index.isIndexCreated())) {
  console.error('No index found. Run `npm run ingest` first.')
  process.exit(1)
}

const results = await index.queryItems(await embed(query), query, limit)

console.log(
  JSON.stringify(
    results.map((r) => ({ score: r.score, metadata: r.item.metadata })),
    null,
    2
  )
)
