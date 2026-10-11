import type { Text, Paragraphs, GameFields, Condition, Variant } from './types'

function conditionMatches(condition: Condition = {}, fields: GameFields): boolean {
  return Object.entries(condition).every(([field, values]) =>
    values.includes(fields[field] ?? ''),
  )
}

export function resolveVariant(text: Text, fields: GameFields): Variant | null {
  if (typeof text === 'string') return { text }
  if (Array.isArray(text)) {
    return text.find(variant => conditionMatches(variant.if, fields)) ?? null
  }
  return conditionMatches(text.if, fields) ? text : null
}

export function resolveText(text: Text, fields: GameFields): string | null {
  return resolveVariant(text, fields)?.text ?? null
}

export function resolveParagraphs(paragraphs: Paragraphs, fields: GameFields): Variant[] {
  return paragraphs.flatMap(p => {
    const resolved = resolveVariant(p, fields)
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
