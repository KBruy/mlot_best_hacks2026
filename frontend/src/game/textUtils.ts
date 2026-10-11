import type { Text, Paragraphs, GameFields, Condition } from './types'

function conditionMatches(condition: Condition = {}, fields: GameFields): boolean {
  return Object.entries(condition).every(([field, values]) =>
    values.includes(fields[field] ?? ''),
  )
}

export function resolveText(text: Text, fields: GameFields): string | null {
  if (typeof text === 'string') return text
  if (Array.isArray(text)) {
    for (const variant of text) {
      if (conditionMatches(variant.if, fields)) return variant.text
    }
    return null
  }
  return conditionMatches(text.if, fields) ? text.text : null
}

export function resolveParagraphs(paragraphs: Paragraphs, fields: GameFields): string[] {
  return paragraphs.flatMap(p => {
    const resolved = resolveText(p, fields)
    return resolved !== null ? [resolved] : []
  })
}

export function resolveTeaser(paragraphs: Paragraphs): string | null {
  for (const p of paragraphs) {
    const resolved = resolveText(p, {})
    if (resolved) return resolved
  }
  return null
}
